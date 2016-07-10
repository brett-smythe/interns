import os
import logging
import logging.config
import time

import celery
from celery.utils.log import get_task_logger


logging_dir = '/tmp/logs'


def get_logger(module_name):
    """Get a celery logger with created with values from settings/logging.conf
    and using time.gmtime.
    """
    logging_dir_check(logging_dir)
    logger = get_task_logger(module_name)
    add_timed_rotation_handler(logger)
    return logger


def add_timed_rotation_handler(logger):
    """Takes the given logger object and adds a timed file rotation handler"""
    rotatingHandler = logging.handlers.TimedRotatingFileHandler(
        '/tmp/logs/interns.log', 'midnight',1 ,0
        , 'utf-8', False, True
    )
    add_formatter_to_handler(rotatingHandler)


def add_formatter_to_handler(handler):
    """Take a handler and adds a handler to it"""
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    formatter.converter = time.gmtime
    handler.setFormatter(formatter)


def logging_dir_check(directory):
    """Checks to see if directory exists, if it does not it attempts to create
    """
    logging_dir = os.path.dirname(directory)
    if not os.path.exists(logging_dir):
        os.makedirs(logging_dir)

