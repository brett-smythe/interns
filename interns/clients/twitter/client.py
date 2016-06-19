import sys, traceback

from interns.settings import interns_settings
from interns.clients.db_client import GetDBSession
from interns.clients.twitter import utils as twitter_utils
from interns.creds import config as creds_config

from aquatic_twitter import client as twitter_client

#from connection import twitter_api

# TODO move this into settings
write_to_memcache = True
if interns_settings.debug:
    write_to_memcache = False
    
twitterClient = twitter_client.AquaticTwitter(
    creds_config.twitter_consumer_key,
    creds_config.twitter_consumer_secret,
    creds_config.twitter_access_token_key,
    creds_config.twitter_access_token_secret,
    write_to_memcache
)

def get_new_user_timeline_tweets(screen_name):
    """
    Pull as many tweets as possible for a newly added user
    """
    #TODO add logging
    timeline_tweets = twitterClient.get_timeline_tweets(screen_name)
    if not interns_settings.debug:
        for tweet in timeline_tweets:
            try:
                twitter_utils.insert_tweet_data(tweet)
            except Exception as e:
                print 'Error: {0}'.format(e)
                exc_type, exc_value, exc_tb = sys.exc_info()
                traceback.print_exception(exc_type, exc_value, exc_tb)
                continue

    else:
        [sys.stdout.write(str(tweet.id) + '\n') for tweet in timeline_tweets]

