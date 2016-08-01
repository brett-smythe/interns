"""Config data for celery"""
from interns.settings import interns_settings
try:
    from interns.creds import config as creds_config
    rabbit_uname = creds_config.rabbit_uname
    rabbit_pwd = creds_config.rabbit_pwd
    rabbitmq_host = interns_settings.rabbitmq_host
    rabbitmq_port = interns_settings.rabbitmq_port
except ImportError:
    import ConfigParser
    config = ConfigParser.ConfigParser()
    config.read('/etc/opt/interns/interns_auth.cfg')
    rabbit_uname = config.get('RabbitMQ', 'rabbit_uname')
    rabbit_pwd = config.get('RabbitMQ', 'rabbit_pwd')
    rabbitmq_host = config.get('RabbitMQ', 'rabbit_host')
    rabbitmq_port = config.get('RabbitMQ', 'rabbit_port')

BROKER_URL = 'amqp://{0}:{1}@{2}:{3}//'.format(
    rabbit_uname,
    rabbit_pwd,
    rabbitmq_host,
    rabbitmq_port
)
