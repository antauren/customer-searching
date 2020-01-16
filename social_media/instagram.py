from collections import Counter
import datetime as dt
from tqdm import tqdm
from instabot import Bot

from utils.datetime import get_the_beginning


def get_stat(research_username, username, password, days_count=90):
    bot = Bot()
    bot.login(username=username, password=password)

    user_id = bot.get_user_id_from_username(research_username)

    media_ids = [id_ for id_ in bot.get_total_user_medias(user_id)]

    media_ids = tqdm(media_ids)

    media_comments_dict = {media_id: bot.get_media_comments_all(media_id)
                           for media_id in media_ids}

    today = get_the_beginning(dt.datetime.now())
    start_date = today - dt.timedelta(days=days_count)

    filtered_media_comments_dict = {media_id: filter_comments_by_date(comments, start_date)
                                    for media_id, comments in media_comments_dict.items()}

    comments_top_users_ids = get_comments_top_users_ids(filtered_media_comments_dict)
    posts_top_users_ids = get_posts_top_users_ids(filtered_media_comments_dict)

    return {
        'comments_top_users_ids': comments_top_users_ids,
        'posts_top_users_ids': posts_top_users_ids
    }


def filter_comments_by_date(comments, date):
    filtered_comments = []

    for comment in comments:
        timestamp = comment['created_at_utc']
        if dt.datetime.utcfromtimestamp(timestamp) < date:
            continue
        filtered_comments.append(comment)

    return filtered_comments


def get_comments_top_users_ids(media_comments: dict) -> Counter:
    counter = Counter()

    for comments in media_comments.values():
        counter.update(comment['user_id'] for comment in comments)

    return counter


def get_posts_top_users_ids(media_comments: dict) -> Counter:
    counter = Counter()

    for comments in media_comments.values():
        unique_user_ids = {comment['user_id'] for comment in comments}
        counter.update(unique_user_ids)

    return counter


def is_user_exist(username, bot):
    return bool(bot.get_user_id_from_username(username))
