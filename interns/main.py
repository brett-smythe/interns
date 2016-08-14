"""Main entry point for interns scheduling service. Currently written to only
be sinle threaded and single instanced. If this is changed the limitation
checks will also need to be re-written
"""
import signal
from time import sleep
from multiprocessing import Process, Queue

from interns.tasks_scheduling.twitter import jobs
from interns.settings import interns_settings
from interns import utils


logger = utils.get_scheduler_logger(__name__)


class Scheduler(object):
    """Class for running scheduled jobs"""

    def __init__(self):
        self.service_running = True
        self.run_scheduler()

    def signal_handler(self, signum, frame):
        """Handle SIGTERM and SIGKILL"""
        # pylint: disable=unused-argument
        self.service_running = False

    def run_scheduler(self):
        """
        The main entry point for the interns scheduling service, starts and
        maintains all of the various timing jobs
        """
        logger.info('Starting interns scheduler')
        logging_queue = Queue()
        workerLogger = utils.MultiProcessLogger(logging_queue, logger)
        twitter_jobs_queue = Queue()
        twitter_jobs_worker = Process(
            target=jobs.TwitterJobs, args=(twitter_jobs_queue, logging_queue)
        )
        twitter_jobs_worker.daemon = True
        twitter_jobs_worker.start()
        try:
            while self.service_running:
                # Check to see if the process was killed
                signal.signal(signal.SIGTERM, self.signal_handler)
                # Some call to check if the service should keep running
                workerLogger.write_log_messages()
                sleep(0.5)
        finally:
            logger.info('Shutting down interns scheduler')
            twitter_jobs_queue.put(interns_settings.process_poison)
            twitter_jobs_worker.join()

if __name__ == '__main__':
    Scheduler()
