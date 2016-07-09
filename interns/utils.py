import os
import logging
import logging.config
import time

import celery
from celery.utils.log import get_task_logger


def get_logger(module_name):
    """Get a celery logger with created with values from settings/logging.conf
    and using time.gmtime.
    """
    here = os.path.abspath(os.path.dirname(__file__))
    #logging_conf_path = '{0}/{1}'.format(here, 'settings/logging.conf')
    logging_conf_path = '{0}/{1}'.format(here, 'settings/interns_lg.conf')
    logging.config.fileConfig(logging_conf_path)
    logging.Formatter.converter = time.gmtime
    logger = get_task_logger(module_name)
    return logger

