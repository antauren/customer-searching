from functools import partial
from tqdm import tqdm
import requests
import datetime as dt

from utils.datetime import get_the_beginning

VERSION_API = 5.103
URL_API_METHOD = 'https://api.vk.com/method'


def get_group_id(domain, access_token) -> int:
    '''https://vk.com/dev/groups.getById'''

    method_name = 'groups.getById'

    params = {
        'group_id': domain,
        'access_token': access_token,
        'v': VERSION_API
    }

    response = requests.get('{}/{}'.format(URL_API_METHOD, method_name), params=params)
    raise_for_status(response)

    return response.json()['response'][0]['id']


def get_top_ids(access_token, posts, owner_id, days_count=14) -> set:
    today = get_the_beginning(dt.datetime.now())
    start_date = today - dt.timedelta(days=days_count)

    top_ids = set()
    for post in posts:
        likers = fetch_all_items(
            func=partial(get_likers, access_token=access_token, owner_id=post['owner_id'], item_id=post['id'])
        )
        liker_ids = set(likers)

        comments = fetch_all_items(
            func=partial(get_wall_comments, access_token, post['id'], owner_id)
        )
        comments = filter(is_not_deleted, comments)
        comments = filter(
            partial(is_comment_posted_later_than_date, date=start_date),
            comments
        )
        commenter_ids = {comment['from_id'] for comment in comments}

        top_ids.update(commenter_ids & liker_ids)

    return top_ids


def fetch_all_items(func, max_count=100):
    tmp_offset = 0
    while True:
        response = func(count=max_count, offset=tmp_offset)

        if tmp_offset > response['count']:
            break

        tmp_offset += max_count

        yield from response['items']


def get_likers(access_token, owner_id, item_id, type='post', skip_own=1, count=1000, offset=0):
    '''https://vk.com/dev/likes.getList'''

    method_name = 'likes.getList'

    params = {

        'owner_id': owner_id,
        'item_id': item_id,
        'type': type,
        'skip_own': skip_own,
        'count': count,
        'offset': offset,

        'access_token': access_token,
        'v': VERSION_API
    }
    response = requests.get('{}/{}'.format(URL_API_METHOD, method_name), params=params)
    raise_for_status(response)

    return response.json()['response']


def get_wall_posts(access_token, owner_id, count=100, offset=0, filter='owner'):
    '''https://vk.com/dev/wall.get'''

    method_name = 'wall.get'

    params = {
        'access_token': access_token,
        'v': VERSION_API,
        'owner_id': owner_id,
        'count': count,
        'offset': offset,
        'filter': filter
    }

    response = requests.get('{}/{}'.format(URL_API_METHOD, method_name), params=params)
    raise_for_status(response)

    return response.json()['response']


def get_wall_comments(access_token, post_id, owner_id, count=100, offset=0):
    '''https://vk.com/dev/wall.getComments'''

    method_name = 'wall.getComments'

    params = {'access_token': access_token,
              'v': VERSION_API,
              'count': count,
              'offset': offset,
              'post_id': post_id,
              'owner_id': owner_id
              }

    response = requests.get('{}/{}'.format(URL_API_METHOD, method_name), params=params)
    raise_for_status(response)

    return response.json()['response']


def is_not_deleted(comment):
    return 'deleted' not in comment


def is_comment_posted_later_than_date(comment, date):
    timestamp = comment['date']
    return dt.datetime.utcfromtimestamp(timestamp) >= date


def get_stat(access_token, domain, days_count):
    group_id = get_group_id(domain, access_token)

    owner_id = -group_id

    posts = fetch_all_items(
        func=partial(get_wall_posts, access_token, owner_id)
    )

    posts = list(posts)
    posts = tqdm(posts)

    top_ids = get_top_ids(access_token, posts, owner_id, days_count)

    return {'top_ids': top_ids}


class VkError(Exception):
    def __init__(self, text):
        self.txt = text


def raise_for_status(response):
    response.raise_for_status()

    resp_dict = response.json()
    if 'error' in resp_dict:
        vk_error = VkError(resp_dict['error']['error_msg'])
        raise vk_error
