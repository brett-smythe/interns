from interns.creds import config as creds_config
from interns.settings import interns_settings

BROKER_URL = 'amqp://{0}:{1}@{2}:{3}//'.format(
    creds_config.rabbit_uname,
    creds_config.rabbit_pwd,
    interns_settings.rabbitmq_host,
    interns_settings.rabbitmq_port
)

