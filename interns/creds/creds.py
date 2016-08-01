"""Creds loader for interns"""
from interns.settings import interns_settings
try:
    # Running in dev mode
    from interns.creds import config as creds_config
    # RabbitMQ
    rabbit_uname = creds_config.rabbit_uname
    rabbit_pwd = creds_config.rabbit_pwd
    rabbitmq_host = interns_settings.rabbitmq_host
    rabbitmq_port = interns_settings.rabbitmq_port
    # Twitter Auth
    twitter_consumer_key = creds_config.twitter_consumer_key
    twitter_consumer_secret = creds_config.twitter_consumer_secret
    twitter_access_token_key = creds_config.twitter_access_token_key
    twitter_access_token_secret = creds_config.twitter_access_token_secret

except ImportError:
    # Running in prod
    import ConfigParser
    config = ConfigParser.ConfigParser()
    config.read('/etc/opt/interns/interns_auth.cfg')
    # RabbitMQ
    rabbit_uname = config.get('RabbitMQ', 'rabbit_uname')
    rabbit_pwd = config.get('RabbitMQ', 'rabbit_pwd')
    rabbitmq_host = config.get('RabbitMQ', 'rabbit_host')
    rabbitmq_port = config.get('RabbitMQ', 'rabbit_port')
    # Twitter Auth
    twitter_consumer_key = config.get('Twitter', 'twitter_consumer_key')
    twitter_consumer_secret = config.get('Twitter', 'twitter_consumer_secret')
    twitter_access_token_key = config.get(
        'Twitter',
        'twitter_access_token_key'
    )
    twitter_access_token_secret = config.get(
        'Twitter',
        'twitter_access_token_secret'
    )
