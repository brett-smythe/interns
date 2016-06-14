from clients.twitter import client as twitter_client

def test():
    twitter_client.get_new_user_timeline_tweets('NASA')

