import os
from request import make_twitter_request
from json_tools import save_json
import argparse

def tweetscrape(screen_name=None, api_route='tweets', max_results=3200):
    assert (screen_name != None), 'Must have screen_name'

    kw = {  # Keyword args for the Twitter API call
        'count': 200,
        'since_id' : 1,
        'screen_name': screen_name,
    }

    max_pages = 16
    results = []

    response = make_twitter_request(api_route, **kw)

    if response is None: # 401 (Not Authorized) - Need to bail out on loop entry
        response = []

    results = response
    total = len(response)
    if api_route == 'follows':
        results = response['users']
        total = len(response['users'])

    print('Fetched {} {}.'.format(total, api_route))

    page_num = 1

    if max_results == kw['count']:
        page_num = max_pages # Prevent loop entry

    if api_route == 'tweets' or api_route == 'favs':
        while page_num < max_pages and len(response) > 0 and len(results) < max_results:
            kw['max_id'] = min([tweet['id'] for tweet in response]) - 1

            response = make_twitter_request(api_route, **kw)
            results += response

            print('Fetched {} {}.'.format(len(response), api_route))

            page_num += 1

    elif api_route == 'follows':
        while response['next_cursor']:
            kw['cursor'] = response['next_cursor']

            response = make_twitter_request(api_route, **kw)
            results += response['users']

            print('Fetched {} {}.'.format(len(response['users']), api_route))

    print('Done fetching {}. Found {} in total.'.format(api_route, len(results[:max_results])))

    return results[:max_results]

def save_tweetscrape(user, route):
    directory = 'data/{}'.format(route)
    if not os.path.exists(directory):
        os.makedirs(directory)

    results = tweetscrape(screen_name=user, api_route=route)
    save_json(route, user, results)



if __name__ == '__main__':
    # parse cli arguments
    ap = argparse.ArgumentParser()
    ap.add_argument('-u', '--user', help='user to scrape (screen name or id)')
    ap.add_argument('-t', '--tweets', help='scrape tweets', action='store_true')
    ap.add_argument('-f', '--favs', help='scrape favs', action='store_true')
    ap.add_argument('-fo', '--following', help='scrape following', action='store_true')
    args = vars(ap.parse_args())

    user = args['user']

    route = 'tweets'
    if args['favs']:
        route = 'favs'
    if args['following']:
        route = 'follows'

    save_tweetscrape(user, route)
