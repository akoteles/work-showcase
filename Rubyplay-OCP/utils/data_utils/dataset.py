import multiprocessing
import os

from typing import (
    Callable,
    Dict,
    Optional,
)

import tensorflow as tf


def load_dataset(path: str, pipeline: Callable,
                 is_train: bool,
                 shuffle_buffer_size: Optional[int] = 1024,
                 batch_size: int = 128,
                 **kwargs) -> tf.data.Dataset:
    wildcard = os.path.join(path, '*.tfrecord')

    dataset = tf.data.Dataset.list_files(wildcard) \
        .interleave(tf.data.TFRecordDataset,
                    multiprocessing.cpu_count())
    dataset = pipeline(dataset, is_train=is_train,
                       shuffle_buffer_size=shuffle_buffer_size,
                       batch_size=batch_size, **kwargs)

    return dataset


def load_datasets(path: str, pipeline: Callable,
                  shuffle_buffer_size: Optional[int] = 1024,
                  batch_size: int = 128,
                  **kwargs) -> Dict[str, tf.data.Dataset]:
    walk = os.walk(path)

    _, nested_dirs, _ = next(walk)
    expected_splits = {'train', 'val', 'test'}

    if set(nested_dirs) != expected_splits:
        raise ValueError('Expected data folds')

    result = {k: load_dataset(os.path.join(path, k), pipeline,
                              is_train=(k == 'train'),
                              shuffle_buffer_size=shuffle_buffer_size,
                              batch_size=batch_size, **kwargs)
              for k in expected_splits}

    return result
