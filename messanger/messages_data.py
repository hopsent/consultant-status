class MessagesData:
    """
    Устанавливает типовые значения, используемые для отправления сообщений.
    """

    COMMON = {
        'access_denied': 'Доступ запрещен. Сорри',
        'reduce_frequency': 'Пожалуйста, следуй правилу: одна команда в 12 секунд',  # noqa
        'all_busy': 'сорри, таких нет - все заняты.',
        'wipe': 'Сбой! Не могу зайти ни в один из аккаунтов! Попробуй позже или проверь самостоятельно',  # noqa
    }

    BEGINNINGS = {
        'normal': 'Попробуй эти аккаунты ',
        'trouble': 'Проблемы с аккаунтами: ',
        'lost_data': 'Есть потерянные аккаунты! Проверены: ',
    }

    ACCOUNT_TYPES = {
        'general': 'общего назначения: ',
        'regional': 'с региональным контентом: ',
    }

    DEFAULT_CHAT = 000000000
