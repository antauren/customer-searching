import sys
from functools import partial
import requests
from collections import Counter
from tqdm import tqdm
import datetime as dt

sys.path.append('..')
from utils.datetime import get_the_beginning

VERSION = 'v5.0'


def fetch_reactions(post_id, token):
    '''https://developers.facebook.com/docs/graph-api/reference/v5.0/object/reactions'''

    params = {
        'access_token': token,
        'fields': 'type'
    }

    response = requests.get('https://graph.facebook.com/{}/{}/reactions'.format(VERSION, post_id), params=params)
    response.raise_for_status()

    return response.json()['data']


def fetch_comments(post_id, token, summary=True):
    '''https://developers.facebook.com/docs/graph-api/reference/v5.0/object/comments'''

    params = {
        'access_token': token,
        'summary': summary
    }
    response = requests.get('https://graph.facebook.com/{}/{}/comments'.format(VERSION, post_id), params=params)
    response.raise_for_status()

    return response.json()['data']


def fetch_posts(group_id, token):
    '''https://developers.facebook.com/docs/graph-api/reference/v5.0/group/feed'''

    params = {
        'access_token': token,
        'fields': 'feed'
    }

    response = requests.get('https://graph.facebook.com/{}/{}/'.format(VERSION, group_id), params=params)
    response.raise_for_status()

    return response.json()['feed']['data']


def get_reactions_counter(posts, token):
    reactions_counter = Counter()

    for post in posts:
        reactions = fetch_reactions(post['id'], token)

        reactions_counter.update(reaction['type'] for reaction in reactions)

    return reactions_counter


def is_published_later_than_date(item: dict, date, key: str) -> bool:
    date_str = item[key]

    date_dt = dt.datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S%z')

    return dt.datetime.timestamp(date_dt) >= dt.datetime.timestamp(date)


def get_top_commenters_ids(posts, start_date, token) -> set:
    all_comments = []
    for post in posts:
        for comment in fetch_comments(post['id'], token):
            all_comments.append(comment)

    filtered_comments = filter(partial(is_published_later_than_date, date=start_date, key='created_time'),
                               all_comments)

    top_commenters_ids = set(comment['from']['id'] for comment in filtered_comments)

    return top_commenters_ids


def get_reactions_counter_from_date(posts, start_date, token):
    filtered_posts = filter(partial(is_published_later_than_date, date=start_date, key='updated_time'),
                            posts)
    return get_reactions_counter(filtered_posts, token)


def get_stat(group_id, token, days_count=30) -> dict:
    posts = fetch_posts(group_id, token)
    posts = tqdm(posts)

    today = get_the_beginning(dt.datetime.now())

    start_date = today - dt.timedelta(days=days_count)

    return {
        'reactions': get_reactions_counter_from_date(posts, start_date, token),
        'top_commenters_ids': get_top_commenters_ids(posts, start_date, token)
    }