"""Utilities for interns twitter client"""
from eleanor_client.endpoints import twitter as eleanor_twitter

from interns.utils import get_celery_logger

# logger = get_logger(__name__)
logger = get_celery_logger(__name__)


def get_tracked_twitter_tl_users():
    """
    Pull the list of twitter users that is being polled by the interns
    """
    logger.debug('Getting listing of tracked twitter users')
    tracked_users = eleanor_twitter.get_tracked_twitter_users()
    return tracked_users


def begin_tracking_twitter_user(username):
    """
    Add a twitter user to be tracked to the databse

    Arguments:
    username -- Twitter username/screen_name to be added. For example to add
    username '@NASA' to be polled: add_tracked_twitter_tl_user('NASA')
    """
    logger.debug('Adding twitter user %s to be tracked', username)
    eleanor_twitter.track_new_twitter_user(username)


def is_twitter_user_in_interns(screen_name):
    """
    Checks to see if a twitter user exists within the database. Returns True
    if the screen_name is present in the database else returns False.

    For example checking to see if the user '@NASA' exists within the database
    the method would be called like so: is_twitter_user_in_interns('NASA')

    Arguments:
    screen_name -- Twitter user_name/screen_name to check for.
    """
    screen_names = get_tracked_twitter_tl_users()
    logger.debug(
        (
            'Twitter username %s  is currently being '
            'tracked by interns is: %s'
        ),
        screen_name,
        screen_name in screen_names
    )
    return screen_name in screen_names


def last_twitter_user_entry_id(screen_name):
    """
    Returns the latest tweet id assocaited with screen_name otherwise returns
    None.

    Arguments:
    screen_name -- Twitter user_name/screen_name to check for.
    """
    last_entry_id = eleanor_twitter.get_username_last_tweet_id(screen_name)
    return last_entry_id


def insert_tweet_data(tweet):
    """
    Adds a tweet to the database

    Arguments:
    tweet -- The tweet object pulled from the twitter library. Some (very)
    limited documentation is located here:
    https://python-twitter.readthedocs.io/en/latest/twitter.html#twitter.models.Status
    """
    logger.debug('Making call to eleanor to add tweet data')
    base_twitter_url = 'https://twitter.com/{0}/status/{1}'
    source_url = base_twitter_url.format(tweet.user.screen_name, tweet.id_str)

    user_mentions = [user.screen_name for user in tweet.user_mentions]
    hashtags = [hashtag.text for hashtag in tweet.hashtags]
    tweet_urls = [url.expanded_url for url in tweet.urls]

    retweet_data = {}
    if tweet.retweeted_status is not None:
        retweet = tweet.retweeted_status
        is_retweet = True
        retweet_url = base_twitter_url.format(
            retweet.user.screen_name,
            tweet.id_str
        )
        retweet_data["user_name"] = retweet.user.screen_name
        retweet_data["tweet_id"] = retweet.id_str
        retweet_data["url"] = retweet_url
        retweet_data["tweet_text"] = retweet.text
        retweet_data["tweet_created"] = retweet.created_at
        retweet_data["is_retweet"] = False

        user_mentions = [user.screen_name for user in retweet.user_mentions]
        retweet_data["user_mentions"] = user_mentions

        hashtags = [hashtag.text for hashtag in retweet.hashtags]
        retweet_data["hashtags"] = hashtags

        tweet_urls = [url.expanded_url for url in retweet.urls]
        retweet_data["tweet_urls"] = tweet_urls
    else:
        is_retweet = False

    tweet_data = {
        "user_name": tweet.user.screen_name,
        "tweet_id": tweet.id_str,
        "url": source_url,
        "tweet_text": tweet.text,
        "tweet_created": tweet.created_at,
        "is_retweet": is_retweet,
        "user_mentions": user_mentions,
        "hashtags": hashtags,
        "tweet_urls": tweet_urls,
        "retweet_data": retweet_data
    }
    eleanor_twitter.add_tweet_data(tweet_data)
