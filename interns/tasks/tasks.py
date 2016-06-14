from interns.settings import interns_settings
from interns.creds import config as creds_config
from interns.clients.twitter import utils as twitter_utils

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
def add(x, y):
    return x + y


@app.task
def track_twitter_user(username):
   twitter_utils.begin_tracking_twitter_user(username)

