from dbConnect import SQLDBConnect
import weatherConnect
import logging
import threading
import time
import sys

from config import *
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters


def get_msg(place):
    place = place.capitalize()
    logger.info(f"Find place")
    is_cached = dbc.get_cached_place(place)
    if is_cached:
        logger.info(f'get {place} from CacheDB')
        msg_text = outMsg.format(*is_cached)
    else:
        logger.info(f'get {place} from WeatherAPI')
        is_exists = weatherConnect.get_weather_data(place)

        if is_exists:
            logger.info(f'Add or update {place} to cache')
            msg_text = outMsg.format(*is_exists)
            dbc.add_place(*is_exists)
        else:
            logger.info(f'{place} is not found')
            msg_text = f'{place} is not found'

    return msg_text


def help_callback(bot, update):
    update.message.reply_text(helpText)


def error_callback(bot, update, error):
    logger.warning('Update "%s" caused error "%s"', update, error)


def set_callback(bot, update, args):
    user_id = update.message.chat_id
    logger.info(user_id)

    try:
        place = args[0]
        subs_period = args[1]
        msg_text = get_msg(place)
        dbc.add_user(user_id, subs_period)
        dbc.add_sub(user_id, place)
    except IndexError:
        msg_text = helpText

    bot.send_message(chat_id=user_id, text=msg_text)


def get_callback(bot, update, args):
    user_id = update.message.chat_id
    logger.info(user_id)

    try:
        place = args[0]
        msg_text = get_msg(place)
    except IndexError:
        msg_text = helpText

    bot.send_message(chat_id=user_id, text=msg_text)


def msg_callback(bot, update):
    user_id = update.message.chat_id
    place = update.message.text
    logger.info(user_id)
    msg_text = get_msg(place)
    bot.send_message(chat_id=user_id, text=msg_text)


def send_weather(update):
    while True:
        logger.info('Trigger sendWeather')
        for user_id, place in dbc.get_subs_user_place():
            msg_text = get_msg(place)
            update.bot.send_message(chat_id=user_id, text=msg_text)
        time.sleep(10)


if __name__ == '__main__':

    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
    logger = logging.getLogger(__name__)

    dbc = SQLDBConnect('data.db')
    dbc.connect()
    if sys.argv and sys.argv[1] == 'new':
        dbc.drop_tables()
        dbc.create_tables()
    updater = Updater(botToken)

    updater.dispatcher.add_handler(CommandHandler('start', help_callback))
    updater.dispatcher.add_handler(CommandHandler('help', help_callback))
    updater.dispatcher.add_handler(CommandHandler('get', get_callback, pass_args=True))
    updater.dispatcher.add_handler(CommandHandler('set', set_callback, pass_args=True))
    updater.dispatcher.add_handler(MessageHandler(Filters.text, msg_callback))
    updater.dispatcher.add_error_handler(error_callback)

    thr = threading.Thread(target=send_weather, args=(updater,))
    thr.start()

    updater.start_polling()
    updater.idle()
    dbc.disconnect()
