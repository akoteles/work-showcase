"""Fit the model.
"""
import copy
import functools
import glob
import importlib
import json
import logging
import os
import re
import shutil
import sys

from argparse import ArgumentParser

from typing import (
    Callable,
    List,
    NoReturn,
    Optional,
    Tuple,
    Union,
)

import tensorflow.keras as keras

from utils.data_utils.dataset import load_datasets

_log = logging.getLogger('client_games-train')

logging.basicConfig(level=logging.INFO)

_DEFAULT_SHUFFLE_BUFFER = 1024
_DEFAULT_BATCH_SIZE = 128
_DEFAULT_OPTIMIZER = 'SGD'
_DEFAULT_OPTIMIZER_ARGS = '{}'
_DEFAULT_CHECKPOINTS_PERIOD = 10

_CHECKPOINT_FILE_NAME_PATTERN = 'model_checkpoint_epoch{}.h5'
_CHECKPOINT_FILE_NAME_PATTERN_CALLBACK = _CHECKPOINT_FILE_NAME_PATTERN.format(
    '{epoch:05d}')

_MODEL_INFO_FILE_NAME = 'model_info.json'


def _make_optimizer(optimizer: str,
                    optimizer_args: dict) -> keras.optimizers.Optimizer:
    """Create a model optimizer instance.

    Arguments:
        optimizer: A name of an optimizer class from `keras.optimizers` module.
        optimizer_args: A dictionary of arguments to be passed to an optimizer
            class constructor.

    Returns:
        An optimizer class instance.
    """
    cls = getattr(keras.optimizers, optimizer, None)

    if cls is None:
        raise ValueError(f'Cannot get an optimizer class by name: {optimizer}')

    optimizer = cls(**optimizer_args)

    return optimizer


def _extract_epoch(checkpoint_file_name: str) -> int:
    """Given a checkpoint file name, extract an epoch number.

    Arguments:
        checkpoint_file_name: A file name of a model checkpoint dump.

    Returns:
        An epoch number.
    """
    pattern = _CHECKPOINT_FILE_NAME_PATTERN.format(r'(\d+)')
    groups = re.search(pattern, checkpoint_file_name)
    epoch = groups.group(1)
    epoch = int(epoch)
    return epoch


def _get_last_checkpoint(
        checkpoints_path: str,
        load_model: bool = False,
        custom_objects: Optional[dict] = None,
) -> Tuple[Optional[Union[str, keras.models.Model]], int]:
    """Given a checkpoints destination path, find out the last checkpoint, if
    any.

    Arguments:
        checkpoints_path: A path to checkpoints destination.

    Returns:
        A tuple of the last checkpoint file name (or `None` if none) and a
        number of an epoch, on which this checkpoint was dumped (0 if none of
        checkpoints were found).
    """
    checkpoints_ext = os.path.splitext(_CHECKPOINT_FILE_NAME_PATTERN)[1]
    checkpoint_files = os.path.join(checkpoints_path, f'*{checkpoints_ext}')
    checkpoint_files = glob.glob(checkpoint_files)
    checkpoint_files = sorted(checkpoint_files)
    model = None

    if len(checkpoint_files) == 0:
        epoch = 0
    else:
        if load_model:
            model = keras.models.load_model(checkpoint_files[-1],
                                            custom_objects=custom_objects)
        epoch = _extract_epoch(checkpoint_files[-1])

    return model, epoch


def _checkpoints_path(model_path: str) -> str:
    return os.path.join(model_path, 'checkpoints')


def _logs_path(model_path: str) -> str:
    return os.path.join(model_path, 'logs')


def _dest_model_path(model_path: str) -> str:
    return os.path.join(model_path, 'model.h5')


def _model_cleanup(model_path: str) -> NoReturn:
    checkpoints_path = _checkpoints_path(model_path)

    _, epoch = _get_last_checkpoint(checkpoints_path)

    print('You are asking not to resume training the model for a given '
          f'destination path: "{model_path}".')
    print(f'The model had been fit for {epoch} epochs.')

    while True:
        response = input('Are you sure you want to drop all the '
                         'checkpoints and metadata for this model? [y/N] ')
        response = response or 'n'

        if response.lower() in ('y', 'n'):
            break

    if response == 'y':
        _log.warning('Removing all the files from the model target '
                     'path: "%s"', model_path)
        shutil.rmtree(model_path)
    else:
        sys.exit(-1)


def _get_model(model_path: str,
               make_model_fn: Callable,
               custom_objects: dict,
               retrain: bool = False) -> Tuple[keras.models.Model, int]:
    if retrain and os.path.exists(model_path):
        _model_cleanup(model_path)

    _log.warning('Using model destination directory: "%s"', model_path)

    if not os.path.exists(model_path):
        _log.info('Making model destination directory')
        os.mkdir(model_path, 0o755)

    checkpoints_path = _checkpoints_path(model_path)

    _log.info('Model checkpoint destination directory: "%s"', checkpoints_path)

    if not os.path.exists(checkpoints_path):
        _log.info('Making checkpoints directory')
        os.mkdir(checkpoints_path, 0o755)

    model, epoch = _get_last_checkpoint(checkpoints_path,
                                        load_model=True,
                                        custom_objects=custom_objects)

    if model is None:
        assert epoch == 0
        model = make_model_fn()

    return model, epoch


def _parse_optional_json_str(data: Optional[str]) -> dict:
    data = data or '{}'
    data = json.loads(data)
    return data


def _dump_model_info(
        model_path: str,
        objective: str,
        model_args: dict,
        optimizer: str,
        optimizer_args: dict,
        splits_path: str,
        shuffle_buffer_size: Optional[int],
        batch_size: int
) -> NoReturn:
    model_args = copy.copy(model_args)
    del model_args['optimizer']

    info = {
        'objective': objective,
        'model_args': model_args,
        'optimizer': {
            'class': optimizer,
            'optimizer_args': optimizer_args,
        },
        'dataset': {
            'splits_path': splits_path,
            'shuffle_buffer_size': shuffle_buffer_size,
            'batch_size': batch_size,
        },
    }

    file_name = os.path.join(model_path, _MODEL_INFO_FILE_NAME)

    if not os.path.exists(file_name):
        _log.info('Writing model info into "%s"', file_name)

        with open(file_name, 'w') as f:
            json.dump(info, f)
    else:
        _log.info('Model info file exists, skipping writing it')


def _make_callbacks(
        model_path: str,
        checkpoints_period: int = 10,
        early_stopping: bool = False
) -> List[keras.callbacks.Callback]:
    callbacks = list()

    if early_stopping:
        callbacks.append(keras.callbacks.EarlyStopping())

    log_dir = _logs_path(model_path)
    _log.info('TensorBoard logs will be written to "%s"', log_dir)

    if not os.path.exists(log_dir):
        os.mkdir(log_dir, 0o755)

    callbacks.append(keras.callbacks.TensorBoard(log_dir=log_dir,
                                                 histogram_freq=10,
                                                 write_grads=True))

    checkpoints_path = _checkpoints_path(model_path)
    checkpoints_pattern = os.path.join(checkpoints_path,
                                       _CHECKPOINT_FILE_NAME_PATTERN_CALLBACK)

    callbacks.append(
        keras.callbacks.ModelCheckpoint(checkpoints_pattern, verbose=1,
                                        period=checkpoints_period))

    return callbacks


def train_model(
        objective: str,
        model_path: str,
        model_args: dict,
        splits_path: str,
        shuffle_buffer_size: int,
        batch_size: int,
        epochs: int,
        retrain: bool,
        early_stopping: bool,
        checkpoints_period: int,
        optimizer: str,
        optimizer_args: dict,
) -> NoReturn:
    objective_module = importlib.import_module(f'objectives.{objective}')
    optimizer_instance = _make_optimizer(optimizer, optimizer_args)
    datasets = load_datasets(splits_path, objective_module.pipeline,
                             shuffle_buffer_size=shuffle_buffer_size,
                             batch_size=batch_size)

    model_args = copy.copy(model_args)
    model_args.update(
        objective_module.model_config_from_dataset(datasets['train']))
    model_args['optimizer'] = optimizer_instance
    make_model_fn = functools.partial(objective_module.make_model,
                                      **model_args)
    model, epoch = _get_model(model_path, make_model_fn,
                              objective_module.custom_objects,
                              retrain=retrain)

    _dump_model_info(model_path, objective, model_args, optimizer,
                     optimizer_args, splits_path, shuffle_buffer_size,
                     batch_size)

    initial_epoch = epoch
    epochs = epoch + epochs
    callbacks = _make_callbacks(model_path,
                                checkpoints_period=checkpoints_period,
                                early_stopping=early_stopping)

    model.fit(datasets['train'], initial_epoch=initial_epoch, epochs=epochs,
              callbacks=callbacks, validation_data=datasets['val'])

    model_file_name = _dest_model_path(model_path)
    model.save(model_file_name)


def _make_parser() -> ArgumentParser:
    parser = ArgumentParser(description=__doc__)

    g = parser.add_argument_group('Dataset')
    g.add_argument('--shuffle-buffer-size', type=int,
                   default=_DEFAULT_SHUFFLE_BUFFER,
                   help='A size of the shuffling buffer for a dataset '
                        'pipeline. [default: %(default)s]')

    g = parser.add_argument_group('Network')
    g.add_argument('--model-args', default=None,
                   help='Depending on the objective, models may have '
                        'different parameters. Pass a valid JSON with parameters '
                        'to be forwarded to a model creation function (depending '
                        'on the objective you chose).')

    g = parser.add_argument_group('Training')
    g.add_argument('--batch-size', type=int, default=_DEFAULT_BATCH_SIZE,
                   help='Batch size to be used. [default: %(default)s]')
    g.add_argument('--epochs', type=int, required=True,
                   help='The number of epochs to train. In case if training '
                        'is resumed, it\'s the number of epochs to be fit in '
                        'addition, not in total.')
    g.add_argument('--early-stopping', action='store_true',
                   help='Exploit early stopping strategy.')
    g.add_argument('--retrain', action='store_true',
                   help='Retrain an existing model.')
    g.add_argument('--checkpoints-period', type=int,
                   default=_DEFAULT_CHECKPOINTS_PERIOD,
                   help='Model checkpoints period in epochs. '
                        '[default: %(default)s]')

    g = parser.add_argument_group('Optimizer')
    g.add_argument('--optimizer', default=_DEFAULT_OPTIMIZER,
                   help='A Keras optimizer class name. [default: %(default)s]')
    g.add_argument('--optimizer-args', default=_DEFAULT_OPTIMIZER_ARGS,
                   help='A Keras optimizer constructor arguments in a form '
                        'of a valid JSON string.')

    parser.add_argument('splits_path', help='A path to a directory, which '
                                            'contains all the splits to fit the model. Expected '
                                            'splits are `train`, `val` and `test`.')
    parser.add_argument('model_path', help='A directory to store model in.')

    parser.add_argument('--objective', choices=['wtte'],
                        required=True, help='A network objective. It governs '
                                            'the way data was prepared and dumped to .tfrecord '
                                            'files with `preprocess_raw_data.py` script.')

    return parser


def _prepare_args(args: dict) -> dict:
    """Process command line arguments to make it possible to pass them to
    `train_model()` function.
    """
    args = copy.copy(args)

    args['model_args'] = _parse_optional_json_str(args['model_args'])
    args['optimizer_args'] = _parse_optional_json_str(args['optimizer_args'])

    return args


if __name__ == '__main__':
    parser = _make_parser()
    args = _prepare_args(vars(parser.parse_args()))
    train_model(**args)
