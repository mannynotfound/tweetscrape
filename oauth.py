import twitter
import io
import json
import random

def oauth_login(index=False):
    with io.open('accounts.json', encoding='utf-8') as f:
        accounts = json.loads(f.read())

    if not index:
        index = random.randrange(len(accounts))

    config = accounts[index]

    CONSUMER_KEY = config.get('consumer_key')
    CONSUMER_SECRET = config.get('consumer_secret')
    ACCESS_TOKEN = config.get('access_token_key')
    ACCESS_TOKEN_SECRET = config.get('access_token_secret')

    auth = twitter.oauth.OAuth(ACCESS_TOKEN, ACCESS_TOKEN_SECRET, CONSUMER_KEY, CONSUMER_SECRET)
    twitter_api = twitter.Twitter(auth=auth)
    return twitter_api

