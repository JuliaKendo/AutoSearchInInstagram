import os
import re
import logging
import argparse
from instabot import Bot
from pprint import pprint
from dotenv import load_dotenv

bot = Bot()


def get_users(coment):
    # https://blog.jstassen.com/2016/03/code-regex-for-instagram-username-and-hashtags/
    pattern = r'(?:@)([A-Za-z0-9_](?:(?:[A-Za-z0-9_]|(?:\.(?!\.))){0,28}(?:[A-Za-z0-9_]))?)'
    result = re.findall(pattern, coment)
    return result


def is_user_exist(username):
    user_id = bot.get_user_id_from_username(username)
    return user_id


def get_number_marked_friends(list_of_insta_users):
    return len([username for username in list_of_insta_users if is_user_exist(username)])


def is_user_keep_conditions(comment, likers, subscribers):
    list_of_users = get_users(comment['text'])
    number_marked_friends = get_number_marked_friends(list_of_users)
    return number_marked_friends \
        and str(comment['user_id']) in likers \
        and str(comment['user_id']) in subscribers


def collect_participants(media_content):
    participants = []
    for comment in media_content['comments']:
        user_keep_conditions = is_user_keep_conditions(comment, media_content['likers'], media_content['subscribers'])
        if user_keep_conditions:
            participants.append(comment['user']['username'])
    return participants


def read_from_insta(media_id, post_author):
    subscribers = bot.get_user_followers(post_author)
    likers = bot.get_media_likers(media_id)
    comments = bot.get_media_comments_all(media_id)
    return {'comments': comments, 'likers': likers, 'subscribers': subscribers}


def create_parser():
    parser = argparse.ArgumentParser(description='Параметры запуска скрипта:')
    parser.add_argument('-l', '--link', help='Ссылка на пост инстаграмма')
    parser.add_argument('-a', '--author', help='Автор поста в инстаграмме')
    return parser


def main():
    load_dotenv()
    logging.basicConfig(level=logging.ERROR, filename='log.txt')

    parser = create_parser()
    args = parser.parse_args()
    if not args.link or not args.author:
        print('Некорректно указаны параметры запуска скрипта.')
        return

    try:
        bot.login(username=os.environ.get('INSTA_USER'), password=os.environ.get('INSTA_PASSWORD'))
        media_id = bot.get_media_id_from_link(args.link)
        media_content = read_from_insta(media_id, args.author)
        participants = collect_participants(media_content)
        pprint(set(participants))
    except (SystemExit, AttributeError):
        logging.error('Ошибка получания данных с инстаграмм. Проверьте наличие интернета или логин и пароль.')
    except (KeyError, TypeError, NameError) as error:
        logging.error('Ошибка обработки данных полученных с инстаграмм: {0}'.format(error))


if __name__ == '__main__':
    main()
