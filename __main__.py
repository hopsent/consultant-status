import logging
from logging.handlers import RotatingFileHandler
from os import getenv

from dotenv import load_dotenv
from telegram.ext import CommandHandler, Updater

from messages_handler import general_account_check, regional_account_check


load_dotenv()

handler = RotatingFileHandler(
    'logs/' + __name__ + '.log',
    maxBytes=52428800,
)
logger_main = logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s, %(levelname)s, %(process)d, %(message)s, %(name)s',
    handlers=[handler, ],
)

secret_token = getenv('TOKEN', default='')


def main():
    updater = Updater(token=secret_token)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler('general', general_account_check))
    dispatcher.add_handler(CommandHandler('regional', regional_account_check))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
