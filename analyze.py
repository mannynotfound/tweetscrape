#!/usr/bin/env python
# coding=utf-8
import os
import json_tools
import argparse
import operator
from pprint import pprint
from termcolor import colored

hits = {}

def add_hit(hit, key):
    if not hits.get(hit):
        hits[hit] = {}
    if not hits.get(hit).get(key):
        hits[hit][key] = 0

    hits[hit][key] += 1

def analyze_tweets(tweets):
    for tweet in tweets:
        entities = tweet.get('entities', {})

        if tweet.get('retweeted_status'):
            hit = tweet.get('retweeted_status').get('user').get('screen_name')
            add_hit(hit, 'retweets')
            entities = tweet.get('retweeted_status').get('entities', {})

        if entities.get('user_mentions'):
            for mention in entities.get('user_mentions'):
                hit = mention.get('screen_name')
                add_hit(hit, 'mentions')

def analyze_favs(favs):
    for fav in favs:
        if fav.get('user', {}).get('screen_name'):
            hit = fav.get('user').get('screen_name')
            add_hit(hit, 'favs')
        if fav.get('entities', {}).get('user_mentions'):
            for mention in fav.get('entities').get('user_mentions'):
                hit = mention.get('screen_name')
                add_hit(hit, 'mentions')

def analyze_follows(follows):
    for follow in follows:
        add_hit(follow.get('screen_name'), 'follows')

def analyze(user):
    global hits
    hits = {}
    all_data = {}

    for data in ['tweets', 'favs', 'follows']:
        try:
            all_data[data] = json_tools.load_json(data, user)
        except Exception as e:
            print('NO {} FOUND'.format(data))
            print(e)

    if all_data.get('tweets'):
        analyze_tweets(all_data.get('tweets'))
    if all_data.get('favs'):
        analyze_favs(all_data.get('favs'))
    if all_data.get('follows'):
        analyze_follows(all_data.get('follows'))

    print('')
    print('ANALYZED {0} ==> '.format(user.upper()))
    print('')
    all_hits = {}

    for key in hits:
        if key == user:
            continue
        if not all_hits.get(key):
            all_hits[key] = 0
        for stat in hits[key]:
            all_hits[key] += hits[key][stat]

    all_hits = sorted(all_hits.items(), key=operator.itemgetter(1), reverse=True)
    top_8 = all_hits[:8]
    for t in top_8:
        name = t[0]
        stats = hits[name]
        favs = stats.get('favs', 0)
        retweets = stats.get('retweets', 0)
        mentions = stats.get('mentions', 0)
        follows = '☑️  ' if stats.get('follows') else ''

        def colorize_num(n):
            return colored(str(n), 'yellow')
        def colorize_str(s):
            return colored(str(s), 'white')

        print('{0}{1} | {2} {3} | {4} {5} | {6} {7}'.format(
            follows,
            name,
            colorize_num(retweets),
            colorize_str('RETWEETS'),
            colorize_num(favs),
            colorize_str('FAVS'),
            colorize_num(mentions),
            colorize_str('MENTIONS')
        ))
        print('')

    results = {
        'user': user,
        'top_8': top_8,
    }

    directory = 'data/analyze'
    if not os.path.exists(directory):
        os.makedirs(directory)

    json_tools.save_json('analyze', user, results)

    return [t[0] for t in top_8]

if __name__ == '__main__':
    # parse cli arguments
    ap = argparse.ArgumentParser()
    ap.add_argument('-u', '--user', help='user to scrape (screen name or id)')
    args = vars(ap.parse_args())

    analyzee = args['user']
    analyze(args['user'])
