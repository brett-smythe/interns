"""Config data for celery"""
from interns.creds import creds

BROKER_URL = 'amqp://{0}:{1}@{2}:{3}//'.format(
    creds.rabbit_uname,
    creds.rabbit_pwd,
    creds.rabbitmq_host,
    creds.rabbitmq_port
)
