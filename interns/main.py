import interns.tasks

from interns.clients.twitter import client as twitter_client
from interns.utils import get_logger


def test():
    twitter_client.get_new_user_timeline_tweets('NASA')


if __name__ == '__main__':
    interns.tasks.app.start()
