from interns.settings import interns_settings
from interns.creds import config as creds_config
from interns.clients.twitter import (utils as twitter_utils,
    client as twitter_client)

from celery import Celery

app = Celery(
    'tasks',
    broker='amqp://{0}:{1}@{2}:{3}//'.format(
        creds_config.rabbit_uname,
        creds_config.rabbit_pwd,
        interns_settings.rabbitmq_host,
        interns_settings.rabbitmq_port
    )
)


@app.task
def track_twitter_user(username):
   twitter_utils.begin_tracking_twitter_user(username)


@app.task
def get_user_timeline_tweets(username):
   twitter_client.get_new_user_timeline_tweets(username) 

