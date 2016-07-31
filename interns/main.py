"""Main entry point for interns scheduling service. Currently written to only
be sinle threaded and single instanced. If this is changed the limitation
checks will also need to be re-written
"""
from time import sleep
from multiprocessing import Process, Queue

from interns.tasks_scheduling.twitter import jobs
from interns.settings import interns_settings
from interns import utils


logger = utils.get_logger(__name__)


def run_service():
    """
    The main entry point for the interns scheduling service, starts and
    maintains all of the various timing jobs
    """
    logger.info('Starting interns scheduler')
    service_running = True
    logging_queue = Queue()
    workerLogger = utils.MultiProcessLogger(logging_queue, logger)
    twitter_jobs_queue = Queue()
    twitter_jobs_worker = Process(
        target=jobs.TwitterJobs, args=(twitter_jobs_queue, logging_queue)
    )
    twitter_jobs_worker.start()
    while service_running:
        try:
            # Some call to check if the service should keep running
            workerLogger.write_log_messages()
            sleep(0.5)
        except KeyboardInterrupt:
            print 'Shutting down interns scheduler'
            break
    logger.info('Shutting down interns scheduler')
    twitter_jobs_queue.put(interns_settings.process_poison)
    twitter_jobs_worker.join()


if __name__ == '__main__':
    run_service()
