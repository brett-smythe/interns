import sys, traceback

from interns.settings import interns_settings
from interns.clients.db_client import GetDBSession
from interns.clients.twitter import utils as twitter_utils

from twitter import TwitterError

from connection import twitter_api


def handle_rate_limit(func):
    """
    Handles the inevitability of hitting the twitter API ratelimit
    """
    # TODO: Needs to be able to talk to the scheduler after a failure to
    # add this task back to a pool and communicate that the connection limit
    # was hit.
    def func_wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except TwitterError as e:
            if 'Exceeded connection limit for user' in e.message:
                pass
                # Log and communicate back to scheduler
            else:
                exc_type, exc_val, exc_tb = sys.exc_info()
                raise exc_type, exc_val, exc_tb
    return func_wrapper
                

def handle_twitter_errors(func):
    """
    Handles errors from the twitter API
    """
    def func_wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except TwitterError as e:
            if 'Capacity Error' in e.message:
                # Log and communicate back to scheduler
                pass
            elif 'Technical Error' in e.message:
                # As above log and communicate
                pass
            else:
                exc_type, exc_val, exc_tb = sys.exc_info()
                raise exc_type, exc_val, exc_tb
    return func_wrapper
    

# potentially combine these methods with connection into a class?
@handle_twitter_errors
@handle_rate_limit
def get_new_user_timeline_tweets(screen_name):
    """
    Pull as many tweets as possible for a newly added user
    """
    timeline_tweets = twitter_api.GetUserTimeline(
        screen_name=screen_name, count=5
    )
    # temp write out
    if not interns_settings.debug:
        for tweet in timeline_tweets:
            # Handle exceptions above this?
            twitter_utils.insert_tweet_data(tweet)

#            try:
#                twitter_utils.insert_tweet_data(tweet)
#            except Exception as e:
#            # TODO: Add more logging here
#                print 'Error: {0}'.format(e)
#                exc_type, exc_value, exc_tb = sys.exc_info()
#                traceback.print_exception(exc_type, exc_value, exc_tb)
#                continue
    else:
        [sys.stdout.write(str(tweet.id) + '\n') for tweet in timeline_tweets]


# Change this to polling or updating
#def poll_user_timeline_tweets(screen_name):
#    timeline_tweets = twitter_api.GetUserTimeline(screen_name=screen_name, since_id=734792287163691008)
#    # temp write out
#    if interns_settings.debug:
#        [sys.stdout.write(str(tweet.id) + '\n') for tweet in timeline_tweets]
#
