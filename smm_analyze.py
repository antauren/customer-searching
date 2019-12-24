import argparse
from dotenv import dotenv_values
import pprint

from social_media.facebook import get_stat as get_stat_fb
from social_media.instagram import get_stat as get_stat_ig
from social_media.vk import get_stat as get_stat_vk


def parse_args():
    parser = argparse.ArgumentParser(
        description='''\
        Программа собирает статистику в социальных сетях Instagram, ВКонтакте и Facebook.        
        
        Выдает ID самых активных участников, которые часто лайкают, репостят и комментируют посты.        
        
        По умолчанию:
        Статистика из Instagram считается за 3 месяца.
        Статистика из ВКонтакте считается за 2 недели.
        В статистике из ВКонтакте только комментаторы, которые лайкали посты.
        В статистике из Facebook есть все комментаторы и все реакции на посты за последний месяц.
        '''
    )
    parser.add_argument('social_media', help='Выберите социальную сеть', choices=['facebook', 'vk', 'instagram'])
    parser.add_argument('-d', '--days', type=int, help='количество дней')

    return parser.parse_args()


if __name__ == '__main__':
    dotenv_dict = dotenv_values()

    args = parse_args()

    if args.social_media == 'vk':
        days_count = args.days or 14

        res = get_stat_vk(access_token=dotenv_dict['VK_APP_TOKEN'],
                          domain=dotenv_dict['VK_RESEARCH_DOMAIN'],
                          days_count=days_count)

    elif args.social_media == 'facebook':
        days_count = args.days or 30

        res = get_stat_fb(group_id=dotenv_dict['FB_GROUP_ID'],
                          token=dotenv_dict['FB_TOKEN'],
                          days_count=days_count)

    elif args.social_media == 'instagram':
        days_count = args.days or 90

        res = get_stat_ig(research_username=dotenv_dict['IG_RESEARCH_USERNAME'],
                          username=dotenv_dict['IG_USERNAME'],
                          password=dotenv_dict['IG_PASSWORD'],
                          days_count=days_count)
    else:
        res = 'Данная программа не поддерживает социальную сеть "{}"'.format(args.social_media)

    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(res)
