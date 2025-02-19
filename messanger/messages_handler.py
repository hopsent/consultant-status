from os import getenv
from datetime import datetime, timezone
from time import sleep

from dotenv import load_dotenv

from core.commander import Commander
from core.status import Status
from core.combiner import Combiner
from messanger.container import PreviuosMessageContainer
from messanger.messages_data import MessagesData as MD


load_dotenv()


# Создаем браузеры и аккаунты.
drivers_regional = Combiner(True).combine_driver_with_account()
drivers_general = Combiner(False).combine_driver_with_account()


# Создаем объект для хранения времени предыдущего запроса и ответа.
previous_message = PreviuosMessageContainer()
previous_response = PreviuosMessageContainer(datetime.now(tz=timezone.utc))

# Подгружаем информацию о референтных значениях чат-айди из .env,
# используем их для валидации пользователей и контроля за исполнением кода.
trouble_handle_id = int(getenv('TROUBLE_CHAT_ID', default=MD.DEFAULT_CHAT))
valid_chat_id = int(getenv('VALID_CHAT_ID', default=MD.DEFAULT_CHAT))


def send_reduce_frequency(context, chat):
    """
    Сообщаем, что нужно увеличить интервал отправки команд боту.
    """
    context.bot.send_message(
        chat_id=chat.id,
        text=f'{MD.COMMON["reduce_frequency"]}'
    )


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
    if regional:
        acc_type = MD.ACCOUNT_TYPES["regional"]
        drivers = drivers_regional
    else:
        acc_type = MD.ACCOUNT_TYPES["general"]
        drivers = drivers_general

    accounts = Commander(regional=regional).perform_not_busy(drivers)

    if 'lost_data' in accounts.keys():
        context.bot.send_message(
            chat_id=trouble_handle_id,  # Отправляем их в чат тех.поддержке.
            text=f'{MD.BEGINNINGS["lost_data"]}'
                 f'{accounts[Status.NO_DATA]}, {accounts[Status.NOT_BUSY]}, '
                 f'{accounts[Status.BUSY]}'
        )

    if len(accounts[Status.BUSY]) + len(accounts[Status.NOT_BUSY]) == 0:
        msg = MD.COMMON["wipe"]
    else:
        msg = f'{MD.BEGINNINGS["normal"]}{acc_type}{busy_msg_chunk(accounts)}'

    # Если есть необработанные аккаунты.
    if accounts[Status.NO_DATA]:
        context.bot.send_message(
            chat_id=trouble_handle_id,  # Отправляем их в чат тех.поддержке.
            text=f'{MD.BEGINNINGS["trouble"]}{accounts[Status.NO_DATA]}'
        )
        if msg != MD.COMMON["wipe"]:
            msg += f'{MD.BEGINNINGS["trouble_ui"]}{accounts[Status.NO_DATA]}'

    previous_response.date = datetime.now(tz=timezone.utc)
    return context.bot.send_message(chat_id=chat.id, text=msg)


def chat_validation(chat):
    """
    Валидируем чат, где будет работать бот, на соответствие
    референтному чату из .env-файла.
    """
    return chat.id == valid_chat_id or chat.id == trouble_handle_id


def date_validation(date: datetime):
    """
    Запрещаем отправку команд со скоростью < одной команды
    раз в 12 секунд. Время приведено в Unix timestamp.
    """
    delta = date - previous_message.date
    if (delta.total_seconds() > 12) and (previous_message.date < previous_response.date):  # noqa.
        previous_message.date = date
        return True
    return False


def common_account_check(update, context, regional):
    date = update.message['date']
    chat = update.effective_chat
    if not chat_validation(chat):
        return send_access_restricted_message(context, chat)
    if not date_validation(date):
        return send_reduce_frequency(context, chat)

    else:
        return check_status_send_message(chat, context, regional=regional)


def general_account_check(update, context):
    """
    Действия бота в случае написания в чате команды /general.
    Если чат не валидный, сообщаем, что доступ запрещен.
    В противном случае сообщаем статус запрошенных аккаунтов.
    """
    return common_account_check(update, context, regional=False)


def regional_account_check(update, context):
    """
    Действия бота в случае написания в чате команды /regional.
    Если чат не валидный, сообщаем, что доступ запрещен.
    В противном случае сообщаем статус запрошенных аккаунтов.
    """
    return common_account_check(update, context, regional=True)
