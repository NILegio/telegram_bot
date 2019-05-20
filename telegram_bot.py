import telebot 
import time
import eventlet
import logging
import requests
import os


THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
TOKEN_VK = ''
SINGLE_RUN = '1'

URL_VK = ''.\
    format(TOKEN_VK)
FILENAME_VK = os.path.join(THIS_FOLDER, 'last_known_id.txt')
BASE_POST_URL = '' #все записи вввввв


BOT_TOKEN = ''
CHANNEL_NAME = '@my_test_bot_group_42'


bot = telebot.TeleBot(BOT_TOKEN)


def get_data():
    timeout = eventlet.Timeout(10)
    try:
        feed = requests.get(URL_VK)
        return feed.json()
    except eventlet.timeout.Timeout:
        logging.warning('Got Timeout retrieving VK JSON data. Cancelling...')
        return None
    finally:
        timeout.cancel()


def send_new_posts(items, last_id):
    for item in items:
        if item['id'] <= last_id:
            break
        link = '{!s}{!s}'.format(BASE_POST_URL, item['id'])
        bot.send_message(CHANNEL_NAME, link)
        time.sleep(1)
    return


def check_new_posts_vk():
    logging.info('[VK] Started scanning for new posts')
    with open(FILENAME_VK, 'rt') as file:
        last_id = int(file.read())
        if last_id is None:
            logging.error('Could not read from storage. Skipped iteration.')
            return
        logging.info('Last ID(VK) = {!s}'.format(last_id))
    try:
        feed = get_data()
        if feed is not None:
            entries = feed['response']['items']
            try:
                tmp = entries[0]['is_pinned']
                send_new_posts(entries[1:], last_id)
            except KeyError:
                send_new_posts(entries, last_id)

            with open(FILENAME_VK, 'wt') as file:
                try:
                    tmp = entries[0]['is_pinned']
                    file.write(str(entries[1]['id']))
                    logging.info('New last_id (VK) is {!s}'.format((entries[1]['id'])))
                except KeyError:
                    file.write(str(entries[0]['id']))
                    logging.info('New last_id (VK) is {!s}'.format((entries[0]['id'])))
    except Exception as ex:
        logging.error('Exception of type {!s} in check_new_post(): {!s}'.format(type(ex).__name__, str(ex)))
        pass
    logging.info('[VK] Finished scanning')
    return



if __name__ == '__main__':
    logging.getLogger('requests').setLevel(logging.CRITICAL)
    logging.basicConfig(format='[%(asctime)s] %(filename)s:%(lineno)d %(levelname)s - %(message)s', level=logging.INFO,
                        filename=os.path.join(THIS_FOLDER, 'bot_log.log'), datefmt='%d.%m.%Y %H:%M:%S')
    if not SINGLE_RUN:
        while True:
            check_new_posts_vk()
            logging.info('[App] Script went to sleep.')
            time.sleep(60*4)
    else:
        check_new_posts_vk()
    logging.info('[App] Script went to sleep.')




