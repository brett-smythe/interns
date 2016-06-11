import twitter

from interns.creds import config as creds_config


twitter_api = twitter.Api(
    consumer_key=creds_config.twitter_consumer_key,
    consumer_secret=creds_config.twitter_consumer_secret,
    access_token_key=creds_config.twitter_access_token_key,
    access_token_secret=creds_config.twitter_access_token_secret
)
