from interns.clients.twitter import client as twitter_client

from interns.utils import get_logger

import interns.tasks

#logger = get_logger(__name__)

def test():
    #logger.debug('Test logging message')
    twitter_client.get_new_user_timeline_tweets('NASA')


if __name__ == '__main__':
    interns.tasks.app.start()
