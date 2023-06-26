class MessagesData:
    """
    Устанавливает типовые значения, используемые для отправления сообщений.
    """

    COMMON = {
        'access_denied': 'Доступ запрещен. Сорри',
        'all_busy': 'сорри, таких нет - все заняты.'
    }

    BEGINNINGS = {
        'normal': 'Попробуй эти',
        'trouble': 'Проблемы с аккаунтами: '
    }

    ACCOUNT_TYPES = {
        'general': 'общие: ',
        'regional': 'региональные: ',
    }

    DEFAULT_CHAT = 000000000
