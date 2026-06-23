import logging
import logging.config

from typing import (
    NoReturn,
)

import yaml


_log = logging.getLogger('client_games_logger')


def configure_logging(log_config_file: str) -> NoReturn:
    with open(log_config_file, 'rt') as f:
        config = yaml.safe_load(f)

    try:
        logging.config.dictConfig(config)
    except Exception as e:
        _log.warning('Cannot load logging configuration file "%s": %s',
                     log_config_file, e)
        logging.basicConfig(level=logging.DEBUG)
