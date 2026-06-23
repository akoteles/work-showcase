from datetime import datetime, timedelta

from airflow.models import Variable, DAG
from commercial.utils.bigquery import execute_single_DML

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2019, 1, 1),
    'email': ['airflow@example.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 0,
    'catchup': False,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG('cube_notif', default_args=default_args, schedule_interval=None)

ENV = Variable.get('ENV')

daily_sql = """
update `acme-data-dev.supervision_microstrategy.t_info_flow`

SET process_flag="CUBES_WAIT", last_update_time=DATETIME(TIMESTAMP '{{ ts }}')

WHERE flow_code='PALP-Quotidien'
""" % ENV

weekly_sql = """
update `acme-data-dev.supervision_microstrategy.t_info_flow`

SET process_flag="CUBES_WAIT", last_update_time=DATETIME(TIMESTAMP '{{ ts }}')

WHERE flow_code='PALP-Hebdomadaire' AND EXTRACT(DAYOFWEEK from DATE '{{ ds }}') = 7
""" % ENV
update_daily = execute_single_DML('update_daily_microstrat_notif', sql=daily_sql, dag=dag)

update_weekly = execute_single_DML('update_weekly_microstrat_notif', sql=weekly_sql, dag=dag)

update_daily >> update_weekly
