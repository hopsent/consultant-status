import logging
import os

from telegram import ReplyKeyboardMarkup
from telegram.ext import CommandHandler, Updater
from dotenv import load_dotenv

from commander import Commander
from core.drivers import DriversHandler


load_dotenv()

logger_main = logging.basicConfig(
    filename='logs/consultant-bot.log',
    level=logging.DEBUG,
    format='%(asctime)s, %(levelname)s, %(process)d, %(message)s, %(name)s'
)

drivers_handler = DriversHandler()
drivers_handler.create_drivers()
drivers = drivers_handler.drivers

secret_token = os.getenv('TOKEN', default='5451439535:AAG6K-x8-ZLEtB7wOOsVjqOYmpNFAOV2TQE')

def common_account_check(update, context):
    chat = update.effective_chat
    context.bot.send_message(
         chat_id=chat.id,
         text=f'{Commander(regional=False).perform_not_busy(drivers)}'
    )

def regional_account_check(update, context):
    chat = update.effective_chat
    context.bot.send_message(
         chat_id=chat.id,
         text=f'{Commander(regional=True).perform_not_busy(drivers)}'
    )

def wake_up(update, context):
    chat = update.effective_chat
    name = update.message.chat.first_name
    context.bot.send_message(
        chat_id=chat.id,
        text=f'Привет, {name}! Какой аккаунт К+ тебя интересует?'
    )
    buttons = ReplyKeyboardMarkup(
        [['Общий', 'Регион']],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    context.bot.send_message(
        chat_id=chat.id,
        text='Сейчас будет готово',
        reply_markup=buttons
    )
#    markup = ReplyKeyboardMarkup.from_column(buttons.keyboard)

def main():
    updater = Updater(token=secret_token)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler('start', wake_up))
    dispatcher.add_handler(CommandHandler('general', common_account_check))
    dispatcher.add_handler(CommandHandler('region', regional_account_check))
  #  dispatcher.add_handler(MessageHandler(Filters.text(buttons), common_db))
  #  dispatcher.add_handler(CommandHandler('Региональная база', regional_db))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
    for driver in drivers:
        driver.quit()
