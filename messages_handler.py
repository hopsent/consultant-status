from os import getenv

from dotenv import load_dotenv

from commander import Commander
from core.drivers import DriversHandler
from core.status import Status
from messages_data import MessagesData as MD


load_dotenv()


# Создаем объект, управляющий загрузкой и поддержанием
# веб-браузера.
drivers_handler = DriversHandler()
drivers_handler.create_drivers()
drivers = drivers_handler.drivers

# Подгружаем информацию о референтных значениях чат-айди из .env,
# используем их для валидации пользователей и контроля за исполнением кода.
trouble_handle_id = int(getenv('TROUBLE_CHAT_ID', default=MD.DEFAULT_CHAT))
valid_chat_id = int(getenv('VALID_CHAT_ID', default=MD.DEFAULT_CHAT))


def send_access_restricted_message(context, chat):
    """
    Сообщаем, что доступа к боту нет, всем тем, кто будет
    активировать бота в собственных чатах, отличных от
    валидного чата.
    """
    context.bot.send_message(
        chat_id=chat.id,
        text=f'{MD.COMMON["access_denied"]}'
    )


def busy_msg_chunk(accounts):
    """
    Разделяем сообщения в зависимости от наличия хотя бы одного
    доступного аккаунта: если аккаунтов нет вообще, направляем
    стандартное сообщение об этом.
    """
    if accounts[Status.NOT_BUSY]:
        return accounts[Status.NOT_BUSY]
    return MD.COMMON["all_busy"]


def check_status_send_message(chat, context, regional):
    """
    На интерфейсе Commander используем метод perform_not_busy(),
    получая в результате словарь со свободными аккаунтами
    (то есть объект Account(status='not_busy') и теми,
    чей статус не выяснен по причине ошибок
    (то есть объект Account(status=None)).
    """
    accounts = Commander(regional=regional).perform_not_busy(drivers)
    if regional:
        acc_type = MD.ACCOUNT_TYPES["regional"]
    else:
        acc_type = MD.ACCOUNT_TYPES["general"]
    context.bot.send_message(
        chat_id=chat.id,
        text=f'{MD.BEGINNINGS["normal"]}{acc_type}{busy_msg_chunk(accounts)}'
    )
    # Если есть необработанные аккаунты.
    if accounts[Status.NO_DATA]:
        context.bot.send_message(
            chat_id=trouble_handle_id,  # Отправляем их в чат тех.поддержке.
            text=f'{MD.BEGINNINGS["trouble"]}{accounts[Status.NO_DATA]}'
        )
    if 'lost_data' in accounts.keys():
        context.bot.send_message(
            chat_id=trouble_handle_id,  # Отправляем их в чат тех.поддержке.
            text=f'{MD.BEGINNINGS["lost_data"]}'
                 f'{accounts[Status.NO_DATA]} {accounts[Status.NOT_BUSY]} '
                 f'{accounts[Status.BUSY]}'
        )


def chat_validation(chat):
    """
    Валидируем чат, где будет работать бот, на соответствие
    референтному чату из .env-файла.
    """
    return chat.id == valid_chat_id


def general_account_check(update, context):
    """
    Действия бота в случае написания в чате команды /general.
    Если чат не валидный, сообщаем, что доступ запрещен.
    В противном случае сообщаем статус запрошенных аккаунтов.
    """
    chat = update.effective_chat
    if not chat_validation(chat):
        return send_access_restricted_message(context, chat)
    else:
        return check_status_send_message(chat, context, regional=False)


def regional_account_check(update, context):
    """
    Действия бота в случае написания в чате команды /regional.
    Если чат не валидный, сообщаем, что доступ запрещен.
    В противном случае сообщаем статус запрошенных аккаунтов.
    """
    chat = update.effective_chat
    if not chat_validation(chat):
        return send_access_restricted_message(context, chat)
    else:
        return check_status_send_message(chat, context, regional=True)
