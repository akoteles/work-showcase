"""Preprocess raw data to make it possible to fit neural network with it
depending on the objective.
"""
import itertools
import glob
import multiprocessing
import os
import tempfile

from argparse import ArgumentParser

from typing import (
    Callable,
    Dict,
    List,
    NoReturn,
    Optional,
    Tuple,
)

import tensorflow as tf
import numpy as np

import pyspark.sql.functions as func

from utils.data_utils.pyspark_reader import (
    PySparkDataFrame,
    data_segment_first_session,
    read_data,
)

from utils.data_utils.metadata import (
    collect_metadata,
    dump_metadata,
    read_metadata,
)

from objectives.wtte import prepare_samples as wtte_processor


_processors = {
    'wtte': wtte_processor,
}


def _data_subset(df: PySparkDataFrame, subset: str) -> PySparkDataFrame:
    assert subset in ('all', 'first_session')

    if subset == 'first_session':
        df = data_segment_first_session(df)

    return df


def _parse_splits(splits: str) -> Tuple[List[str], List[float]]:
    def _parse_single_split_info(
            split_info: str) -> Tuple[Optional[str], Optional[float]]:
        split_info = split_info.split(':')
        split_name = None
        split_value = None

        if len(split_info) == 1:
            if split_info[0] != '':
                split_value = float(split_info[0])
        elif len(split_info) == 2:
            split_name = split_info[0]
            split_value = float(split_info[1])
        else:
            raise ValueError('Invalid split information')

        return split_name, split_value

    splits = splits.split(',')

    splits = map(_parse_single_split_info, splits)
    names, splits = zip(*splits)
    splits = list(splits)

    names_all_none = all(name is None for name in names)
    names_all_not_none = all(name is not None for name in names)

    assert names_all_none or names_all_not_none

    if names_all_none:
        splits = [split for split in splits if split is not None]
        names = [f'split_{idx:02d}' for idx in range(len(splits) + 1)]
        assert all(split > 0 and split < 1 for split in splits), \
            'All split values should be within interval (0, 1)'
        assert all(split_left < split_right
                   for split_left, split_right in zip(splits[:-1],
                                                      splits[1:])), \
            'Split values should be given in sorted order with no zero gaps'
    else:
        splits = np.cumsum(splits).tolist()
        assert splits[-1] == 1, 'Named splits values should sum to 1'

    return names, splits


def _make_splits(data: PySparkDataFrame,
                 splits: Tuple[List[str], List[float]],
                 by: str = 'playerId',
                 seed: Optional[int] = None) -> Dict[str, PySparkDataFrame]:
    split_names, split_values = splits
    unique_values = data.select(by) \
                        .distinct() \
                        .sort(func.col(by))
    split_values = [split_values[0], *np.diff(split_values)]
    splits = unique_values.randomSplit(split_values, seed=seed)
    result = {split_name: data.join(split, on=by)
              for split_name, split in zip(split_names, splits)}

    return result


def _make_temp(tmp_dir: Optional[str]) -> tempfile.TemporaryDirectory:
    return tempfile.TemporaryDirectory(dir=tmp_dir)


def _clean_temp(tmp_dir: tempfile.TemporaryDirectory) -> NoReturn:
    tmp_dir.cleanup()


def _dump_metadata(data: PySparkDataFrame, metadata_file_name: str):
    print('Collecting dataset metadata')

    metadata = collect_metadata(data)
    dump_metadata(metadata, metadata_file_name)

    print(f'Metadata was dumped to {metadata_file_name}')

    return metadata_file_name


def _dump_grouped(data: PySparkDataFrame, work_dir: str, splits: str,
                  players_per_tfrecord: int,
                  split_seed: Optional[int] = None) -> dict:
    total_players = data.select('playerId').distinct().count()
    buckets_count = int(round(total_players / players_per_tfrecord))
    buckets_count = max(buckets_count, 1)

    print(f'Total players count: {total_players}')
    print(f'Requested players per tfrecord file: {players_per_tfrecord}')
    print(f'Total buckets count: {buckets_count}')

    print(f'Splitting the dataset')
    splits = _parse_splits(splits)
    splits = _make_splits(data, splits, seed=split_seed)

    split_paths = dict()

    for split_name, split_data in splits.items():
        work_dest_dir = os.path.join(work_dir, split_name)
        split_paths[split_name] = work_dest_dir
        print(f'Temporarily dumping split "{split_name}" to {work_dest_dir}')

        split_data = split_data.withColumn('bucket', func.col('playerId') %
                                           buckets_count)
        split_data.repartition('bucket') \
                  .write \
                  .parquet(work_dest_dir, partitionBy='bucket')

    return split_paths


def _dump_tfrecord(input_file_name: str, output_file_name: str,
                   metadata_file_name: str, samples_fn: Callable) -> NoReturn:
    print(f'Getting ready to dump samples from {input_file_name} '
          f'to {output_file_name}')
    metadata = read_metadata(metadata_file_name)
    samples = samples_fn(input_file_name, metadata)
    count = 0

    with tf.io.TFRecordWriter(output_file_name) as writer:
        for sample in samples:
            writer.write(sample.SerializeToString())
            count += 1

    print(f'There are {count} samples dumped to file "{output_file_name}"')


def _dump_tfrecords(split_path: str, split_dest_path: str,
                    metadata_file_name: str,
                    samples_fn: Callable,
                    n_threads: Optional[int] = None) -> NoReturn:
    files = glob.glob(os.path.join(split_path, '**/*.parquet'))
    files = sorted(files)
    target_file_names = (
        os.path.join(split_dest_path, f'data_{idx:05d}.tfrecord')
        for idx in range(len(files))
    )
    arguments = (
        (input_file_name, output_file_name, metadata_file_name, samples_fn)
        for input_file_name, output_file_name in zip(files, target_file_names)
    )
    n_threads = n_threads or multiprocessing.cpu_count()
    n_threads = min(n_threads, len(files))

    with multiprocessing.Pool(n_threads) as pool:
        pool.starmap(_dump_tfrecord, arguments)


def preprocess_data(data_path: str, dest_path: str, objective: str,
                    splits: Optional[str] = None,
                    tmp_dir: Optional[str] = None,
                    players_per_tfrecord: int = 256,
                    seed: Optional[int] = None,
                    skip_metadata: bool = False,
                    n_threads: Optional[int] = None) -> NoReturn:
    tmp_dir = _make_temp(tmp_dir)
    data = read_data(data_path)

    if not os.path.exists(dest_path):
        os.mkdir(dest_path, 0o755)

    try:
        metadata_file_name = os.path.join(dest_path, 'metadata.json')

        if not skip_metadata:
            _dump_metadata(data, metadata_file_name)

        split_paths = _dump_grouped(data, tmp_dir.name, splits,
                                    players_per_tfrecord, split_seed=seed)
        del data

        samples_fn = _processors[objective]

        for split_name, split_path in split_paths.items():
            split_dest_path = os.path.join(dest_path, split_name)

            if not os.path.exists(split_dest_path):
                os.mkdir(split_dest_path, 0o755)

            print(f'Calculating features for split "{split_name}" from '
                  f'"{split_path}"')

            _dump_tfrecords(split_path, split_dest_path, metadata_file_name,
                            samples_fn, n_threads)
    finally:
        tmp_dir.cleanup()


def _make_parser() -> ArgumentParser:
    parser = ArgumentParser(description=__doc__)

    parser.add_argument('data_path',
                        help='A path to a directory where all the data is '
                        'stored.')
    parser.add_argument('dest_path', help='A path to dump .tfrecord files to.')

    parser.add_argument('--objective', choices=['wtte'],
                        default='wtte',
                        help='An objective of the model. [default: '
                        '%(default)s]')
    parser.add_argument('--splits', default='train:0.6,val:0.2,test:0.2',
                        help='A splits to be made. Either in form '
                        'of comma-separated floating point values in '
                        'ascending order with split points, e.g. 0.6:0.8 '
                        'means that there will be three splits, 0.6 of all '
                        'the histories would go to the first split, 0.2 to '
                        'the second and 0.2 to the third one. Or it would be '
                        'comma-separated of colon-separated tuples, such as '
                        'split_name:split_value. E.g. previous example with '
                        'named splits looks like train:0.6,val:0.2,test:0.2. '
                        'Note that values should sum to 1. '
                        '[default: %(default)s]')
    parser.add_argument('--players-per-tfrecord', type=int, default=256,
                        help='While dumping tfrecord files, how many players '
                        'would be written into one file. '
                        '[default: %(default)s]')
    parser.add_argument('--tmp-dir', default=None,
                        help='A path to a temporary directory. If missing, '
                        'system default is used.')
    parser.add_argument('--seed', type=int, default=None,
                        help='Random seed.')
    parser.add_argument('--skip-metadata', action='store_true',
                        help='Skip metadata calculation and use existing '
                        '`metadata.json` from destination directory.')
    parser.add_argument('--n-threads', type=int, default=None,
                        help='A number of threads to calculate features in. '
                        'If missing, the number of threads is the number of '
                        'cores.')

    return parser


if __name__ == '__main__':
    parser = _make_parser()
    args = parser.parse_args()
    args = vars(args)

    preprocess_data(**args)
