"""Utilities for interns service"""
import os
import logging
import logging.config
import time
import subprocess
import Queue

from celery.utils.log import get_task_logger


def get_logger(module_name):
    """Get a logger with created with values from settings/logging.conf and
    using time.gmtime
    """
    logger = logging.getLogger(module_name)
    logger.setLevel(logging.DEBUG)
    handler = logging.handlers.TimedRotatingFileHandler(
        '/tmp/interns.log', 'midnight', 1, 0, 'utf-8', False, True
    )
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    formatter.converter = time.gmtime
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger


def get_celery_logger(module_name):
    """Get a celery logger with created with values from settings/logging.conf

    and using time.gmtime.
    """
    logger = get_task_logger(module_name)
    add_timed_rotation_handler(logger)
    return logger


def add_timed_rotation_handler(logger):
    """Takes the given logger object and adds a timed file rotation handler"""
    rotatingHandler = logging.handlers.TimedRotatingFileHandler(
        '/tmp/interns.log', 'midnight', 1, 0,
        'utf-8', False, True
    )
    add_formatter_to_handler(rotatingHandler)
    logger.addHandler(rotatingHandler)


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


class MultiProcessCheckingLogger(object):
    """Logger for using where a module may be used by a MP process

    This class currently is only implemented for a *nix based OS. Checks
    with parent process id with 'ps -p {ppid} -o comm=' to see if the result is
    'python'. Depending on what process management is done to keep this running
    this may make things more difficult than expected.
    """

    def __init__(self, logger):
        """
        The logger that is passed in will be used for logging if this isn't
        spawned by a python process
        """
        self.logger = logger

        self.spawned_by_python = True
        self.ppid = os.getppid()
        self.parent_proc_name = subprocess.check_output(
            ["ps", "-p", str(self.ppid), "-o", "comm="]
        )
        if 'python' not in self.parent_proc_name:
            self.spawned_by_python = False

    def should_log_message(self):
        """
        Check to see if a message should be logged
        """
        # This didn't need to be in its own method but if the detection method
        # for this changes this pay for itself later
        return not self.spawned_by_python

    def debug(self, msg):
        """
        Log a debug level log message
        """
        if self.should_log_message():
            self.logger.debug(msg)

    def info(self, msg):
        """
        Log an info level log message
        """
        if self.should_log_message():
            self.logger.info(msg)

    def warning(self, msg):
        """
        Log a warning level log message
        """
        if self.should_log_message():
            self.logger.warning(msg)

    def error(self, msg):
        """
        Log an error level log message
        """
        if self.should_log_message():
            self.logger.error(msg)

    def critical(self, msg):
        """
        Log a critical level log message
        """
        if self.should_log_message():
            self.logger.critical(msg)


class MultiProcessLogger(object):
    """Class for logging with the multiprocessing module

    This is accomplished with an instanced queue that is supplied to the class.
    This class should exist either in the main thread/process *or* be the only
    process writing to logs.

    """

    def __init__(self, queue, logger=None):
        """
        There should only be one instance of this instance that has a logger
        argument supplied
        """
        self.queue = queue
        self.logger = logger

    def put_message_in_queue(self, level, msg, logger_name):
        """Adds logging message to logging queue"""
        try:
            self.queue.put_nowait([level, msg, logger_name])
        except Queue.Full:
            # So this is non optimal *but* in this instance I'm valuing
            # service stability over information available.
            pass

    def debug(self, logger_name, msg):
        """
        Adds a debug level log message to the queue
        """
        self.put_message_in_queue('debug', msg, logger_name)

    def info(self, logger_name, msg):
        """
        Adds an info level log message to the queue
        """
        self.put_message_in_queue('info', msg, logger_name)

    def warning(self, logger_name, msg):
        """
        Adds a warning level log message to the queue
        """
        self.put_message_in_queue('warning', msg, logger_name)

    def error(self, logger_name, msg):
        """
        Adds an error level log message to the queue
        """
        self.put_message_in_queue('error', msg, logger_name)

    def critical(self, logger_name, msg):
        """
        Adds a critical level log message to the queue
        """
        self.put_message_in_queue('critical', msg, logger_name)

    def write_log_messages(self):
        """
        Check the queue for log messages and write them out using the supplied
        logger. If this is called and a logger was not supplised in
        initialization or self.logger is None an AttributeError will be raised
        """
        if self.logger is None:
            raise AttributeError(
                'A logger was not supplied and writing logs was attempted'
            )
        if not self.queue.empty():
            log_info = self.queue.get_nowait()
            level = log_info[0]
            msg = log_info[1]
            self.logger.name = log_info[2]
            if level == 'debug':
                self.logger.debug(msg)
            elif level == 'info':
                self.logger.info(msg)
            elif level == 'warning':
                self.logger.warning(msg)
            elif level == 'error':
                self.logger.error(msg)
            elif level == 'critical':
                self.logger.critical(msg)
