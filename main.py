import os
import re
import time
import logging
import argparse
from instabot import Bot
from pprint import pprint
from dotenv import load_dotenv

bot = Bot()

def get_insta_users(coment):
    pattern = '(?:@)([A-Za-z0-9_](?:(?:[A-Za-z0-9_]|(?:\.(?!\.))){0,28}(?:[A-Za-z0-9_]))?)'
    result = re.findall(pattern, coment)
    return result

def is_user_exist(username):
    user_id = bot.get_user_id_from_username(username)
    return bool(user_id)

def get_number_of_marked_frends(list_of_insta_users):
    return len([is_user_exist(username) for username in list_of_insta_users])

def is_user_meet_requirements(item, likers, subscribers):
    list_of_insta_users = get_insta_users(item['text'])
    number_of_marked_frends = get_number_of_marked_frends(list_of_insta_users)
    if number_of_marked_frends > 0 \
        and str(item['user_id']) in likers \
        and str(item['user_id']) in subscribers:
        return item['user']['username']

def get_users_meet_requirements(info_from_insta):
    users_meet_requirements = []
    for item in info_from_insta['comments']:
        user_meet_requirements = is_user_meet_requirements(item, info_from_insta['likers'], info_from_insta['subscribers'])
        if user_meet_requirements:
            users_meet_requirements.append(user_meet_requirements)
    return users_meet_requirements

def read_from_insta(media_id, post_author):
    subscribers = bot.get_user_followers(post_author)
    likers = bot.get_media_likers(media_id)
    comments = bot.get_media_comments_all(media_id)
    return {'comments':comments, 'likers':likers, 'subscribers':subscribers}

def create_parser():
    parser = argparse.ArgumentParser(description='Параметры запуска скрипта:')
    parser.add_argument('-l', '--link', help='Ссылка на пост инстаграмма')
    parser.add_argument('-a', '--author', help='Автор поста в инстаграмме')
    return parser

def main():
    load_dotenv()
    logging.basicConfig(level = logging.ERROR, filename = 'log.txt')

    parser = create_parser()
    args = parser.parse_args()
    if not args.link or not args.author:
        print('Не корректно указаны параметры запуска скрипта.')
        return

    try:
        bot.login(username=os.environ.get('INSTA_USER'), password=os.environ.get('INSTA_PASSWORD'))
        media_id = bot.get_media_id_from_link(args.link)
        info_from_insta = read_from_insta(media_id, args.author)
        users_meet_requirements = get_users_meet_requirements(info_from_insta)
        pprint(set(users_meet_requirements))
    except (SystemExit, AttributeError):
        logging.error('Ошибка получания данных с инстаграмм. Проверьте наличие интернета или логин и пароль.')
    except (KeyError, TypeError, NameError) as error:
        logging.error('Ошибка обработки данных полученных с инстаграмм: {0}'.format(error))

if __name__=='__main__':
    main()