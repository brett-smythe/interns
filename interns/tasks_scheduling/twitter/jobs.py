"""Process for scheduling Twitter polling jobs for interns"""
import time
import Queue

from interns.tasks import tasks as intern_tasks

from interns.tasks_scheduling.twitter import utils as twitter_utils
from interns.settings import interns_settings
from interns import utils


class TwitterJobs(object):
    """Class for handling the scheduling of interns twitter polling"""

    def __init__(self, job_queue, log_queue):
        self.logger = utils.MultiProcessLogger(log_queue)
        self.logger.info(__name__, 'Starting twitter job scheduler')
        self.job_queue = job_queue
        self.running = True

        self.twitterLimits = twitter_utils.TwitterLimits(
            multi_proc_logger=self.logger
        )
        sleep_secs = self.twitterLimits.get_sleep_between_jobs()
        self.last_execution_time = time.time() - sleep_secs
        self.tracked_twitter_users = (
            twitter_utils.get_tracked_twitter_usernames()
        )
        self.twitter_user_index = 0

        if len(self.tracked_twitter_users) == 0:
            self.running = False

        while self.running:
            if not self.job_queue.empty():
                try:
                    poison_check = self.job_queue.get_nowait()
                except Queue.Empty:
                    poison_check = None
                if poison_check == interns_settings.process_poison:
                    self.logger.info(
                        __name__,
                        'Shutting down twitter job scheduler'
                    )
                    self.running = False
                    continue
            self.execute_next_job()

    def update_tracked_users(self):
        """
        Get tracked twitter usernames
        """
        self.logger.debug(__name__, 'Updating tracked twitter users')
        self.tracked_twitter_users = (
            twitter_utils.get_tracked_twitter_usernames()
        )

    def get_user_timeline_tweets(self, username):
        """
        Pull the timeline tweets from username
        """
        self.logger.info(
            __name__,
            u'Pulling timeline tweets for username {0}'.format(username)
        )
        intern_tasks.get_user_timeline_tweets.delay(username)

    def execute_next_job(self):
        """
        Determines and runs the next fetch job, takes care of sleeping between
        jobs
        """
        self.logger.debug(__name__, 'Updating twitter API limits')
        self.twitterLimits.update_limits()
        sleep_secs = self.twitterLimits.get_sleep_between_jobs()
        self.logger.debug(
            __name__,
            'Updated time to sleep between twitter jobs to {0} seconds'.format(
                sleep_secs
            )
        )
        time_to_execute = (
            (time.time() - self.last_execution_time) >= sleep_secs
        )
        if time_to_execute:
            if self.twitter_user_index >= len(self.tracked_twitter_users):
                self.twitter_user_index = 0
            username = self.tracked_twitter_users[self.twitter_user_index]
            self.get_user_timeline_tweets(username)
            self.last_execution_time = time.time()
            self.twitter_user_index += 1
        else:
            time.sleep(time.time() - self.last_execution_time)
