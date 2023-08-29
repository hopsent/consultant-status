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

secret_token = getenv('TOKEN', default='0')
port = getenv('PORT', default='8443')
ip = getenv('SERVER_ADDRESS', default='0.0.0.0')
cert = getenv('CERT_PATH', default='./cert')
key = getenv('KEY_PATH', default='./key')
listen = getenv('LISTEN', default='0.0.0.0')


def main():
    updater = Updater(token=secret_token)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler('general', general_account_check))
    dispatcher.add_handler(CommandHandler('regional', regional_account_check))
    updater.start_webhook(
        listen=listen,
        port=int(port),
        url_path=secret_token,
        webhook_url='https://' + ip + ':' + port + '/' + secret_token,
        cert=cert,
        key=key,
    )
    updater.idle()


if __name__ == '__main__':
    main()
