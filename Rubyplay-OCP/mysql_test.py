"""Test how data pumping may affect insertion of the data in the database."""
import copy
import datetime
import itertools
import logging
import multiprocessing
import os
import sys
import time

from argparse import ArgumentParser

from multiprocessing import (
    connection,
    Process,
    Pipe,
    Queue,
)

from typing import (
    NoReturn,
    Optional,
    Tuple,
)

import numpy as np
import pandas as pd

from utils.mysql import MySqlConnection

logging.basicConfig(level=logging.DEBUG)

DATABASE_NAME = 'games_db'
TABLE_NAME = 'data_pump_test'
STMT_CREATE_DB = f'CREATE DATABASE IF NOT EXISTS {DATABASE_NAME};'
STMT_DROP_TABLE = f'DROP TABLE IF EXISTS {TABLE_NAME};'
STMT_CREATE_TABLE = '''
CREATE TABLE IF NOT EXISTS {} (
id BIGINT AUTO_INCREMENT NOT NULL,
balance DECIMAL(10, 2) NOT NULL,
win DECIMAL(10, 2) NOT NULL,
bet DECIMAL(10, 2) NOT NULL,
currencyCode CHAR(3) NOT NULL,
deviceType VARCHAR(32) NOT NULL,
gameId INT NOT NULL,
gameSessionId INT NOT NULL,
operatorId INT NOT NULL,
playerId INT NOT NULL,
time DATETIME NOT NULL,
PRIMARY KEY (id)
);
'''.format(TABLE_NAME)

ROW_GENERATORS = {
    'balance': lambda: np.random.uniform(0, 1e6),
    'bet': lambda: np.random.uniform(0, 200),
    'win': lambda: (np.random.choice([0, 1], p=[0.99, 0.01]) *
                    np.random.uniform(0, 2e6)),
    'currencyCode': lambda: np.random.choice(
        ['MYR', 'IDR', 'CNY', 'EUR', 'THB', 'KRW', 'INR', 'USD', 'VND']),
    'deviceType': lambda: np.random.choice(['desktop', 'mobile', 'tablet']),
    'gameId': lambda: np.random.randint(27) + 1,
    'gameSessionId': lambda: np.random.randint(2000000),
    'operatorId': lambda: np.random.randint(4),
    'playerId': lambda: np.random.randint(40000),
    'time': lambda: datetime.datetime.now(),
}


def _enqueue_event(q: Optional[Queue], who: str, event_type: str,
                   timestamp: datetime.datetime,
                   value: Optional[float] = None) -> NoReturn:
    if q is None:
        return

    event = {
        'who': who,
        'event_type': event_type,
        'timestamp': timestamp,
    }

    if value is not None:
        event['value'] = value

    q.put(event)


def _generate_row_insert_stmt() -> Tuple[str, tuple]:
    columns, generators = zip(*ROW_GENERATORS.items())
    fields = ', '.join(columns)
    values = tuple(gen() for gen in generators)
    placeholder = ', '.join(['%s'] * len(columns))
    stmt = f'INSERT INTO {TABLE_NAME} ({fields}) VALUES ({placeholder});'

    return stmt, values


def _writer_loop(mysql_conn_args: dict, freq: float = 1000,
                 report_period: int = 5, commit_each: int = 1,
                 report_queue: Optional[Queue] = None):
    current_process = multiprocessing.current_process()
    log = logging.getLogger(f'db_writer-{current_process.name}')
    logging.basicConfig(level=logging.INFO)

    conn = MySqlConnection(database_name=DATABASE_NAME, **mysql_conn_args)
    sleep_time = 1 / freq if freq else 0
    start = time.time()
    count = 0

    for idx in itertools.count(1):
        stmt, values = _generate_row_insert_stmt()
        conn.exec(stmt, values)

        if idx % commit_each == 0:
            conn.commit()

        count += 1
        time.sleep(sleep_time)
        now = time.time()

        if now - start >= report_period:
            diff = now - start
            performance = count / diff
            log.info('Records write rate: %.4f 1/s', performance)

            _enqueue_event(report_queue, 'writer',
                           f'performance-{current_process.name}', now,
                           performance)

            count = 0
            start = now


def _db_writer(mysql_conn_args: dict,
               pipe_conn: Optional[connection.Connection] = None,
               freq: float = 1000, report_period: int = 5,
               commit_each: int = 1,
               report_queue: Optional[Queue] = None,
               n_processes: Optional[int] = 1) -> NoReturn:
    log = logging.getLogger('db_writer')
    logging.basicConfig(level=logging.INFO)

    conn = MySqlConnection(**mysql_conn_args)

    conn.exec(STMT_CREATE_DB)
    conn.commit()

    conn = MySqlConnection(database_name=DATABASE_NAME, **mysql_conn_args)
    conn.exec(STMT_DROP_TABLE)
    conn.exec(STMT_CREATE_TABLE)
    conn.commit()
    conn.close()

    if pipe_conn:
        pipe_conn.send('ready')
        pipe_conn.close()

    args = (mysql_conn_args, freq, report_period, commit_each, report_queue)

    if n_processes is None or n_processes == 1:
        log.info('Running writing loop in a single process')
        _writer_loop(*args)
    else:
        log.info('Spawning %d writer processes', n_processes)
        processes = [Process(target=_writer_loop, args=args)
                     for _ in range(n_processes)]
        for process in processes:
            process.start()

        for process in processes:
            process.join()


def _dump_file(data: list, file_name: str,
               logger: Optional[logging.Logger] = None) -> NoReturn:
    data = pd.DataFrame(data)
    data.to_csv(file_name, header=False, index=False,
                compression='gzip')

    if logger:
        logger.info('Dumped %d records', data.shape[0])


def _data_pump(mysql_conn_args: dict, dest_dir: str,
               period: int,
               pipe_conn: Optional[connection.Connection] = None,
               report_queue: Optional[Queue] = None,
               start_datetime: Optional[datetime.datetime] = None) -> NoReturn:
    log = logging.getLogger('data_pump')
    logging.basicConfig(level=logging.INFO)

    if pipe_conn is not None:
        msg = pipe_conn.recv()

        if msg != 'ready':
            sys.exit(-1)

    if not os.path.exists(dest_dir):
        os.mkdir(dest_dir, 0o755)

    start = time.time()

    start_datetime = start_datetime or datetime.datetime.now()
    diff = datetime.datetime.now() - start_datetime

    while True:
        time.sleep(period)
        conn = MySqlConnection(database_name=DATABASE_NAME, **mysql_conn_args)

        now = time.time()
        now_dt = datetime.datetime.fromtimestamp(now) - diff

        file_name = os.path.join(dest_dir, 'dump_{}.csv.gz'.format(
            now_dt.strftime('%Y%m%d-%H%M%S')))

        start_dt = datetime.datetime.fromtimestamp(start) - diff

        log.info(f'Dumping data into {file_name}')
        log.info(f'Dumping between {start_dt} and {now_dt}')

        _enqueue_event(report_queue, 'data_pump', 'start', now)

        stmt = f'SELECT * FROM {TABLE_NAME} WHERE time BETWEEN %s AND %s;'
        values = (start_dt, now_dt)

        exec_start = time.time()
        rows = conn.exec(stmt, values)
        _dump_file(rows, file_name, log)
        log.info('Writing file took %.4fms',
                 1000 * (time.time() - exec_start))

        conn.close()

        _enqueue_event(report_queue, 'data_pump', 'end', time.time())

        start = now


def _make_mysql_connection_args(
        host: str = 'db.internal.example.com',
        port: int = 3306,
        user: str = 'db_user',
        password: str = 'PLACEHOLDER_SECRET',
) -> dict:
    args = {
        'host': host,
        'port': port,
        'user': user,
        'password': password,
    }

    return args


def _write_report(timeline: list, file_name: str) -> NoReturn:
    df = pd.DataFrame(timeline)
    df.to_csv(file_name, index=False)


def run_experiment(
        pump_dest_dir: str,
        pump_period: int,
        writer_max_freq: float,
        writer_report_period: int,
        writer_commit_each: int,
        writer_n_processes: int,
        host: str = 'db.internal.example.com',
        port: int = 3306,
        user: str = 'db_user',
        password: str = 'PLACEHOLDER_SECRET',
) -> NoReturn:
    mysql_conn_args = _make_mysql_connection_args(host, port, user, password)
    conn_writer, conn_pump = Pipe()

    log = logging.getLogger('master')
    timeline = list()
    queue = Queue()

    writer = Process(target=_db_writer, args=(mysql_conn_args, conn_writer,
                                              writer_max_freq,
                                              writer_report_period,
                                              writer_commit_each, queue,
                                              writer_n_processes))
    pump = Process(target=_data_pump, args=(mysql_conn_args, pump_dest_dir,
                                            pump_period, conn_pump, queue))

    log.info('Starting writer and data pump processes...')
    writer.start()
    pump.start()

    try:
        while True:
            timeline.append(queue.get())
    except KeyboardInterrupt:
        _write_report(timeline, 'report.csv')
        sys.exit(0)


def _make_parser() -> ArgumentParser:
    parser = ArgumentParser()

    g = parser.add_argument_group('MySQL arguments')
    g.add_argument('--host', default='db.internal.example.com',
                   help='[default: %(default)s]')
    g.add_argument('--port', default=3306, type=int,
                   help='[default: %(default)s]')
    g.add_argument('--user', default='db_user',
                   help='[default: %(default)s]')
    g.add_argument('--password', default='PLACEHOLDER_SECRET',
                   help='[default: %(default)s]')

    g = parser.add_argument_group('Experiment arguments')
    g.add_argument('--pump-dest-dir', default='/tmp',
                   help='[default: %(default)s]')
    g.add_argument('--pump-period', default=30, type=int,
                   help='Dump periodity in seconds. [default: %(default)s]')
    g.add_argument('--writer-max-freq', default=1000, type=float,
                   help='Maximum writes per second. [default: %(default)s]')
    g.add_argument('--writer-report-period', default=5, type=int,
                   help='Writing performance reporting period. '
                        '[default: %(default)s]')
    g.add_argument('--writer-commit-each', default=1, type=int,
                   help='Commit changes to a database each N rows. '
                        '[default: %(default)s]')
    g.add_argument('--writer-n-processes', default=1, type=int,
                   help='Run writer in a given number of processes.')

    return parser


if __name__ == '__main__':
    parser = _make_parser()
    args = parser.parse_args()
    args = vars(args)
    run_experiment(**args)
