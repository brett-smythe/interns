"""Celery tasks for inters workers"""
from celery import Celery

from interns.settings import celeryconfig
from interns.clients.twitter import (
    utils as twitter_utils,
    client as twitter_client
)
from interns.utils import get_celery_logger

logger = get_celery_logger(__name__)


app = Celery('tasks')
app.config_from_object(celeryconfig)


# This may no longer be necessary with eleanor owning db access
@app.task
def track_twitter_user(username):
    """
    When given a username start polling their timeline for tweet data
    """
    logger.info('Adding twitter user %s to tracked users', username)
    twitter_utils.begin_tracking_twitter_user(username)
    if not twitter_utils.is_twitter_user_in_interns(username):
        get_user_timeline_tweets(username)


@app.task
def get_user_timeline_tweets(username):
    """
    Pull the tweets from username's timeline
    """
    logger.info('Polling twitter user %s for timeline tweets', username)
    last_tweet_id = twitter_utils.last_twitter_user_entry_id(username)
    if last_tweet_id:
        twitter_client.get_user_timeline_tweets(
            username, last_tweet_id, logger
        )
    else:
        twitter_client.get_new_user_timeline_tweets(username, logger)

if __name__ == '__main__':
    app.start()
