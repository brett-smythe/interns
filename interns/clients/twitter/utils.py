import sys, traceback

from sqlalchemy import distinct, desc
from sqlalchemy.exc import IntegrityError

from dateutil.parser import parse as date_parse

from interns.clients import utils as interns_utils
from interns.clients.db_client import GetDBSession

from interns.models import models
from interns.models import twitter_models


def get_tracked_twitter_tl_users():
    """
    Pull the list of twitter users that is being polled by the interns
    """
    tracked_users = []
    with GetDBSession() as db_session:
        tracked_users = db_session.query(
            twitter_models.PolledTimelineUsers
        ).all()
    return tracked_users


def add_tracked_twitter_tl_user(username):
    """
    Add a twitter user to be tracked to the databse

    Arguments:
    username -- Twitter username/screen_name to be added. For example to add
    username '@NASA' to be polled: add_tracked_twitter_tl_user('NASA')
    """
    new_user = twitter_models.PolledTimelineUsers(user_name=username)
    with GetDBSession() as db_session:
        db_session.add(new_user)
        db_session.commit()


def is_twitter_user_in_interns(screen_name):
    """
    Checks to see if a twitter user exists within the database. Returns True
    if the screen_name is present in the database else returns False.
    
    For example checking to see if the user '@NASA' exists within the database
    the method would be called like so: is_twitter_user_in_interns('NASA')

    Arguments:
    screen_name -- Twitter user_name/screen_name to check for.
    """
    with GetDBSession() as db_session:
        distinct_screen_names = db_session.query(
            distinct(twitter_models.TwitterSource.tweet_origin_screen_name)
        )
    return screen_name in distinct_screen_names


def last_twitter_user_entry_id(screen_name):
    """
    Returns the latest tweet id assocaited with screen_name otherwise returns
    None.

    Arguments:
    screen_name -- Twitter user_name/screen_name to check for.
    """
    with GetDBSession() as db_session:
        if is_twitter_user_in_interns(screen_name):
            return db_session.query(desc(TwitterSource.tweet_id)).first()
        else:
            return None


def insert_user_mentions(tweet, tweet_model, session):
    """
    Adds user mentions from a tweet to the database

    Arguments:
    tweet -- The tweet object pulled from the twitter library.
    tweet_model -- The TwitterSource object that has already been added to the
    database session but not yet commited.
    session -- The active database session.
    """
    for user in tweet.user_mentions:
        UserMention = twitter_models.TweetUserMentions(
            twitter_source=tweet_model,
            user_name=user.screen_name
        )
        session.add(UserMention)


def insert_hashtags(tweet, tweet_model, session):
    """
    Adds hashtags from a tweet to the database

    Arguments:
    tweet -- The tweet object pulled from the twitter library.
    tweet_model -- The TwitterSource object that has already been added to the
    database session but not yet commited.
    session -- The active database session.
    """
    for hashtag in tweet.hastags:
        TweetHashtags = twitter_models.TweetHashtags(
            twitter_source=tweet_model,
            hashtag=hashtag.text
        )
        session.add(TweetHashtags)


def insert_urls(tweet, tweet_model, session):
    """
    Adds URLs from a tweet to the database

    Arguments:
    tweet -- The tweet object pulled from the twitter library.
    tweet_model -- The TwitterSource object that has already been added to the
    database session but not yet commited.
    session -- The active database session.
    """
    for url in tweet.urls:
        TweetURL = twitter_models.TweetURLs(
            twitter_source=tweet_model,
            url=url.expanded_url
        )
        session.add(TweetURL)


def insert_tweet_data(tweet):
    """
    Adds a tweet to the database and returns the newly created tweet model id
    or None if the tweet has already been captured

    Arguments:
    tweet -- The tweet object pulled from the twitter library. Some (very)
    limited documentation is located here:
    https://python-twitter.readthedocs.io/en/latest/twitter.html#twitter.models.Status
    """
    base_twitter_url = 'https://twitter.com/{0}/status/{1}'
    # If this is a retweet we don't want to store the entry twice (once under
    # the retweeter and then once again under the original tweeter)
    if tweet.retweeted_status is not None:
        # TODO: Add exception handling here to remove the retweeted status
        # on exception here
        retweet = tweet.retweeted_status
        original_tweet_id = insert_tweet_data(retweet)
        if original_tweet_id is None:
            # Already captured, nothing else to do
            return None

        try:

            with GetDBSession() as db_session:
                OriginalTweet = db_session.query(models.TextSource).get(
                    original_tweet_id
                )
                
                original_url = base_twitter_url.format(
                    OriginalTweet.twitter_source.tweeter_user_name,
                    OriginalTweet.twitter_source.tweet_id
                )

                TweetTextModel = interns_utils.insert_text_data(
                    models.AllowedSources.twitter.name,
                    original_url,
                    '',
                    tweet.created_at,
                    db_session
                )
                TweetModel = twitter_models.TwitterSource(
                    text_source=TweetTextModel,
                    retweet_source_id=OriginalTweet.id,
                    tweeter_user_name=tweet.user.screen_name,
                    tweet_id=tweet.id,
                    is_retweet=True
                )
                db_session.commit()
        except IntegrityError as e:
            if 'duplicate key value' in e.message:
                # This tweet has already been captured so:
                return None
            else:
                # TODO logging
                return None
        except Exception as e:
            # Bad stuff happened
            # TODO: Definitely logging here
            return None

        # We don't store the urls/hashtags/mentions as it is all done within
        # the retweet. However this may need to be changed depending on how
        # the twitter API deals with quote tweets or modified tweets (MTs)

    else:
        source_url = base_twitter_url.format(
            tweet.user.screen_name,
            tweet.id
        )
        
        with GetDBSession() as db_session:
            TweetTextModel = interns_utils.insert_text_data(
                models.AllowedSources.twitter.name,
                source_url,
                tweet.text,
                tweet.created_at,
                db_session
            )

            TweetModel = twitter_models.TwitterSource(
                text_source=TweetTextModel,
                tweeter_user_name=tweet.user.screen_name,
                tweet_id=tweet.id,
                is_retweet=False
            )
            try:
                db_session.add(TweetModel)
                db_session.flush()
                tweet_model_id = TweetModel.id

                if tweet.user_mentions != []:
                    insert_user_mentions(tweet, TweetModel, db_session)

                if tweet.hashtags != []:
                    insert_hashtags(tweet, TweetModel, db_session)

                if tweet.urls != []:
                    insert_urls(tweet, TweetModel, db_session)

                db_session.commit()
            except IntegrityError as e:
                if 'duplicate key value' in e.message:
                    # This tweet has already been captured so:
                    return None
                else:
                    # TODO logging
                    return None
            except Exception as e:
                # Bad stuff happened
                # TODO: Definitely logging here
                return None
        return tweet_model_id

