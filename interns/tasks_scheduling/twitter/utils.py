"""Utilities for twitter task scheduling"""
from datetime import datetime, timedelta

from pymemcache.client.base import Client as MemCacheClient

from interns.settings import interns_settings
from interns import utils
from interns.clients.twitter.client import twitterClient

from eleanor_client.endpoints import twitter as eleanor_twitter


epoch_time = datetime(1970, 1, 1)

module_logger = utils.get_logger(__name__)
logger = utils.MultiProcessCheckingLogger(module_logger)


class TwitterLimits(object):
    """
    Checks against either the twitter API or memcached twitter API results for
    twitter API requests limits
    """
    def __init__(self, timeline_rate_reserve=5, multi_proc_logger=None):
        """
        The reserve arguments are how many requests to hold back on to leave
        some form of buffer in place with regards to API limits
        """

        if multi_proc_logger:
            self.logger = multi_proc_logger
        else:
            self.logger = utils.MultiProcessCheckingLogger(module_logger)

        self.memcacheClient = MemCacheClient(
            (interns_settings.memcache_host, interns_settings.memcache_port)
        )

        self.timeline_rate_reserve = timeline_rate_reserve

        self.tl_total_reqs = interns_settings.twitter_timeline_requests
        self.tl_reqs_left = interns_settings.twitter_timeline_req_left
        self.tl_reqs_reset_time = interns_settings.twitter_timeline_reset_time

        self.update_limits()

    def update_limits(self):
        """
        Update the limits associated with the twitter api

        First attempts to check memcache and then checks directly with the
        twitter API
        """
        self.logger.debug(__name__, 'Updating twitter limits')
        cache_total_tl_reqs = self.memcacheClient.get('timeline_limit')
        if cache_total_tl_reqs:
            self.tl_total_reqs = int(cache_total_tl_reqs)

        cache_tl_reqs_left = self.memcacheClient.get('timeline_remaining')
        if cache_tl_reqs_left:
            self.tl_reqs_left = int(cache_tl_reqs_left)

        cache_tl_reqs_reset_time = self.memcacheClient.get(
            'timeline_reset'
        )
        if cache_tl_reqs_reset_time:
            self.tl_reqs_reset_time = int(cache_tl_reqs_reset_time)
            utc_now = datetime.utcnow()
            utc_secs = (utc_now - epoch_time).total_seconds()
            secs_until_reset = self.tl_reqs_reset_time - utc_secs
            if secs_until_reset <= 0:
                # Force getting rates from twitter
                self.tl_reqs_reset_time = None

        update_values_valid = (
            self.tl_total_reqs and
            (self.tl_reqs_left is not None) and
            self.tl_reqs_reset_time
        )

        if not update_values_valid:
            self.logger.debug(__name__, 'Making twitter API limits request')
            update_vals = (
                twitterClient.get_user_timeline_rate_limit()
            )
            self.tl_total_reqs = update_vals.limit
            self.tl_reqs_left = update_vals.remaining
            self.tl_reqs_reset_time = update_vals.reset
        else:
            self.logger.debug(
                __name__,
                'Using twitter API limits from memcache'
            )
        self.logger.debug(
            __name__,
            'Total twitter timeline requests allowed is: {0}'.format(
                self.tl_total_reqs
            )
        )
        self.logger.debug(
            __name__,
            'Number of twitter timeline requests left is: {0}'.format(
                self.tl_reqs_left
            )
        )
        self.logger.debug(
            __name__,
            'Twitter timeline request reset time is: {0}'.format(
                self.tl_reqs_reset_time
            )
        )

    def get_sleep_between_jobs(self):
        """
        Calculate the sleep time between jobs as to not run into the twitter
        API limits
        """
        self.update_limits()
        self.logger.debug(__name__, 'Updating sleep time between jobs')
        utc_now = datetime.utcnow()
        utc_secs = (utc_now - epoch_time).total_seconds()
        self.logger.debug(__name__, 'UTC in seconds {0}'.format(utc_secs))
        secs_until_reset = self.tl_reqs_reset_time - utc_secs
        self.logger.debug(
            __name__,
            'Seconds until API reset {0}'.format(secs_until_reset)
        )
        buffered_tl_reqs_left = (
            self.tl_reqs_left - self.timeline_rate_reserve
        )
        self.logger.debug(
            __name__,
            'Buffered timeline requests left {0}'.format(
                buffered_tl_reqs_left
            )
        )
        if buffered_tl_reqs_left <= 0:
            sleep_time = secs_until_reset
        else:
            sleep_time = secs_until_reset / buffered_tl_reqs_left
        self.logger.debug(__name__, 'Sleep time {0}'.format(sleep_time))
        return sleep_time


class TwitterLimitsTimer(object):
    """Timer class for using the twitter API as either it or the python client
    in use (python-twitter) is getting mixed results from the API. Either way
    the limits are know quantities"""

    def __init__(self, multi_proc_logger, start_time=None,
                 reqs_window_secs=900, number_of_reqs=180):
        """Takes a start_time (utc datetime object) and uses it as the baseline for
        calculating number of twitter requests"""
        if start_time is None:
            start_time = datetime.utcnow()
        self.reqs_window_start = start_time
        self.reqs_window_time = reqs_window_secs
        self.number_of_reqs_per_window = number_of_reqs
        self.reqs_left = number_of_reqs
        self.sleep_time = reqs_window_secs / number_of_reqs
        self.logger = multi_proc_logger

    def calculate_limits(self):
        """Calculate limits with current limits data"""
        rollover_time = self.reqs_window_start + timedelta(
            seconds=self.reqs_window_time
        )
        now = datetime.utcnow()
        if now > rollover_time:
            self.reqs_window_start = rollover_time
            self.reqs_left = self.number_of_reqs_per_window

        time_until_rollover = rollover_time - now
        if self.reqs_left <= 0:
            self.sleep_time = time_until_rollover.seconds
        else:
            self.sleep_time = time_until_rollover.seconds / self.reqs_left
        self.logger.debug(
            __name__,
            'Total twitter timeline requests allowed is: {0}'.format(
                self.number_of_reqs_per_window
            )
        )
        self.logger.debug(
            __name__,
            'Number of twitter timeline requests left is: {0}'.format(
                self.reqs_left
            )
        )
        self.logger.debug(
            __name__,
            'Twitter timeline request reset time is: {0}'.format(
                rollover_time.isoformat()
            )
        )

    def decrement_api_reqs(self):
        """Call this method directly before or after making an api request to
        count the request and calculate the new limits"""
        self.calculate_limits()
        self.reqs_left -= 1


def get_tracked_twitter_usernames():
    """
    Get the usernames that are being tracked on twitter
    """
    logger.debug('Getting tracked twitter user names')
    tracked_twitter_unames = eleanor_twitter.get_tracked_twitter_users()
    return tracked_twitter_unames
