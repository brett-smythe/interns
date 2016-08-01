"""Client for twitter services"""
import sys

from interns.settings import interns_settings
from interns.clients.twitter import utils as twitter_utils
from interns import utils
from interns.creds import creds

from aquatic_twitter import client as twitter_client

write_to_memcache = True
if interns_settings.debug:
    write_to_memcache = False

twitterClient = twitter_client.AquaticTwitter(
    creds.twitter_consumer_key,
    creds.twitter_consumer_secret,
    creds.twitter_access_token_key,
    creds.twitter_access_token_secret,
    write_to_memcache
)


logger = utils.get_logger(__name__)


def get_new_user_timeline_tweets(screen_name):
    """
    Pull as many tweets as possible for a newly added user
    """
    # pylint: disable=expression-not-assigned
    logger.debug(
        'Getting timeline tweets for twitter user: %s',
        screen_name
    )
    timeline_tweets = twitterClient.get_timeline_tweets(screen_name)
    if not interns_settings.debug:
        for tweet in timeline_tweets:
            try:
                twitter_utils.insert_tweet_data(tweet)
            except Exception as e:
                logger.error(
                    (
                        'Error attempting to get twitter user %s '
                        'timeline tweets %s'
                    ),
                    screen_name,
                    e
                )
                continue

    else:
        [sys.stdout.write(str(tweet.id) + '\n') for tweet in timeline_tweets]


def get_user_timeline_tweets(screen_name, last_tweet_id):
    """
    Pull tweets for a user that already has entries in the database
    """
    # pylint: disable=expression-not-assigned
    logger.debug(
        (
            'Getting timline tweets for twitter user %s starting with '
            'tweet id %s'
        ),
        screen_name,
        last_tweet_id
    )
    timeline_tweets = twitterClient.get_timeline_tweets_since_id(
        screen_name,
        last_tweet_id
    )
    if not interns_settings.debug:
        for tweet in timeline_tweets:
            try:
                twitter_utils.insert_tweet_data(tweet)
            except Exception as e:
                logger.error(
                    (
                        'Error attempting to get twitter user %s '
                        'timeline tweets %s'
                    ),
                    screen_name,
                    e
                )
                continue

    else:
        [sys.stdout.write(str(tweet.id) + '\n') for tweet in timeline_tweets]
