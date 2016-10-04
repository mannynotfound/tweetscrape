import io
from urllib2 import URLError
from httplib import BadStatusLine
import sys
import twitter
import time
from oauth import oauth_login
import json
import random
from random import randrange

with io.open('accounts.json', encoding='utf-8') as f:
    accounts = json.loads(f.read())

used_accounts = []

def get_twitter_request(route):
    global used_accounts
    available = filter(lambda x: x not in used_accounts, enumerate(accounts))
    random_index = randrange(0, len(available))
    if len(used_accounts) + 1 == len(accounts):
        used_accounts = [random_index]
    else:
        used_accounts.append(random_index)

    twitter_api = oauth_login(random_index)
    twitter_api_func = twitter_api.statuses.user_timeline

    if route == 'favs':
        twitter_api_func = twitter_api.favorites.list
    elif route == 'follows':
        twitter_api_func = twitter_api.friends.list

    return twitter_api_func

def make_twitter_request(route, max_errors=10, *args, **kw):
    if route == 'tweets':
        kw['include_rts'] = 'true'

    twitter_api_func = get_twitter_request(route)

    def handle_twitter_http_error(e, wait_period=2, sleep_when_rate_limited=True):
        if wait_period > 3600: # Seconds
            print >> sys.stderr, 'Too many retries. Quitting.'
            raise e

        if e.e.code == 401:
            print >> sys.stderr, 'Encountered 401 Error (Not Authorized)'
            return None
        elif e.e.code == 404:
            print >> sys.stderr, 'Encountered 404 Error (Not Found)'
            return None
        elif e.e.code == 429:
            print >> sys.stderr, 'Encountered 429 Error (Rate Limit Exceeded)'
            if sleep_when_rate_limited:
                print >> sys.stderr, "Retrying in 15 minutes...ZzZ..."
                sys.stderr.flush()
                time.sleep(60*15 + 5)
                print >> sys.stderr, '...ZzZ...Awake now and trying again.'
                return 2
            else:
                raise e
        elif e.e.code in (500, 502, 503, 504):
            print >> sys.stderr, 'Encountered %i Error. Retrying in %i seconds' % \
                (e.e.code, wait_period)
            time.sleep(wait_period)
            wait_period *= 1.5
            return wait_period
        else:
            raise e

    # End of nested helper function

    wait_period = 2
    error_count = 0

    while True:
        try:
            return twitter_api_func(*args, **kw)
        except twitter.api.TwitterHTTPError, e:
            error_count = 0
            wait_period = handle_twitter_http_error(e, wait_period)
            if wait_period is None:
                return
        except URLError, e:
            error_count += 1
            print >> sys.stderr, "URLError encountered. Continuing."
            if error_count > max_errors:
                print >> sys.stderr, "Too many consecutive errors...bailing out."
                raise
        except BadStatusLine, e:
            error_count += 1
            print >> sys.stderr, "BadStatusLine encountered. Continuing."
            if error_count > max_errors:
                print >> sys.stderr, "Too many consecutive errors...bailing out."
                raise
