import os
from scrape import save_tweetscrape
from analyze import analyze
import argparse
import json_tools

to_scrape = []

def scrape_single(user):
    for data in ['tweets', 'favs', 'follows']:
        try:
            exists = json_tools.load_json(data, user)
        except Exception as e:
            print('{} - NO {} FOUND... SCRAPIN SOME'.format(user, data))
            save_tweetscrape(user, data)

    return analyze(user)


def add_to_scrape(group):
    counter = 0
    for g in group:
        for data in ['tweets', 'favs', 'follows']:
            try:
                exists = json_tools.load_json(data, g)
            except Exception as e:
                if g not in to_scrape:
                    counter += 1
                    to_scrape.append(g)

    print('ADDED {} TO SCRAPE'.format(counter))


def scrape_group(group):
    print('SCRAPING {} TOTAL'.format(len(group)))
    for g in group:
        scraped_top_8 = scrape_single(g)
        add_to_scrape(scraped_top_8)

    scrape_group(to_scrape)


def scrape_all(user, recursive):
    top_8 = scrape_single(user)
    if recursive:
        scrape_group(top_8)


if __name__ == '__main__':
    # parse cli arguments
    ap = argparse.ArgumentParser()
    ap.add_argument('-u', '--user', help='user to scrape (screen name or id)')
    ap.add_argument('-r', '--recursive', help='crape recursively', action="store_true")
    args = vars(ap.parse_args())

    scrape_all(args['user'], args['recursive'])

