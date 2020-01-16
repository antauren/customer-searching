import sys
from functools import partial
import requests
from collections import Counter, defaultdict
from tqdm import tqdm
import datetime as dt

from utils.datetime import get_the_beginning

VERSION = 'v5.0'


def fetch_reactions(post_id, token):
    '''https://developers.facebook.com/docs/graph-api/reference/v5.0/object/reactions'''

    params = {
        'access_token': token,
        'fields': ['id', 'type']
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


def get_users_reactions(posts, token):
    users_reactions = defaultdict(Counter)

    for post in posts:
        reactions = fetch_reactions(post['id'], token)

        for reaction in reactions:
            user_id = reaction['id']
            reaction_type = reaction['type']

            users_reactions[user_id][reaction_type] += 1

    return users_reactions


def is_published_later_than_date(published_date: str, date) -> bool:
    date_dt = dt.datetime.strptime(published_date, '%Y-%m-%dT%H:%M:%S%z')

    return dt.datetime.timestamp(date_dt) >= dt.datetime.timestamp(date)


def get_top_commenters_ids(posts, start_date, token) -> set:
    all_comments = []
    for post in posts:
        all_comments.extend(fetch_comments(post['id'], token))

    filtered_comments = [comment for comment in all_comments
                         if is_published_later_than_date(comment['created_time'], start_date)]

    top_commenters_ids = {comment['from']['id'] for comment in filtered_comments}

    return top_commenters_ids


def get_reactions_counter_from_date(posts, start_date, token):
    filtered_posts = [post for post in posts
                      if is_published_later_than_date(post['updated_time'], start_date)]

    return get_users_reactions(filtered_posts, token)


def get_stat(group_id, token, days_count=30) -> dict:
    posts = fetch_posts(group_id, token)
    posts = tqdm(posts)

    today = get_the_beginning(dt.datetime.now())

    start_date = today - dt.timedelta(days=days_count)

    return {
        'reactions': get_reactions_counter_from_date(posts, start_date, token),
        'top_commenters_ids': get_top_commenters_ids(posts, start_date, token)
    }
