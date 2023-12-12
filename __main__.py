import logging
from logging.handlers import RotatingFileHandler
from os import getenv

from dotenv import load_dotenv
from telegram.ext import CommandHandler, Updater

from messanger.messages_handler import general_account_check, regional_account_check


load_dotenv()

handler = RotatingFileHandler(
    'logs/' + __name__ + '.log',
    maxBytes=52428800,
)
logger_main = logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s, %(levelname)s, %(process)d, %(message)s, %(name)s',
    handlers=[handler, ],
)

secret_token = getenv('TOKEN', default='0')
server_port = getenv('SERVER_PORT', default='5001')
port = getenv('PORT', default='443')
server_address = getenv('SERVER_ADDRESS', default='0.0.0.0')
listen = getenv('LISTEN', default='0.0.0.0')


def main():
    updater = Updater(token=secret_token)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler('general', general_account_check))
    dispatcher.add_handler(CommandHandler('regional', regional_account_check))
    updater.start_webhook(
        listen=listen,
        port=int(server_port),
        url_path=secret_token,
        webhook_url='https://' + server_address + ':' + port + '/' + secret_token
    )
    updater.idle()


if __name__ == '__main__':
    main()
