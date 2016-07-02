from celery import Celery

from celery.utils.log import get_task_logger

from interns.settings import interns_settings, celeryconfig
from interns.creds import config as creds_config
from interns.clients.twitter import (utils as twitter_utils,
    client as twitter_client)
from interns.utils import get_logger

logger = get_logger(__name__)
#logger = get_task_logger(__name__)

#TODO REMOVE ME
print 'Module name is: {0}'.format(__name__)

app = Celery('tasks')
app.config_from_object(celeryconfig)


@app.task
def track_twitter_user(username):
    """
    When given a username start polling their timeline for tweet data
    """
    logger.info('Adding twitter user {0} to tracked users'.format(username))
    twitter_utils.begin_tracking_twitter_user(username)
    if not twitter_utils.is_twitter_user_in_interns(username):
        get_user_timeline_tweets(username)


@app.task
def get_user_timeline_tweets(username):
    """
    Pull the tweets from username's timeline
    """
    logger.info(
        'Polling twitter user {0} for timeline tweets'.format(username)
    )
    last_tweet_id = twitter_utils.last_twitter_user_entry_id(username)
    if last_tweet_id:
        twitter_client.get_user_timeline_tweets(username, last_tweet_id)
    else:
        twitter_client.get_new_user_timeline_tweets(username)

if __name__ == '__main__':
    app.start()
