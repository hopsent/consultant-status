class MessagesData:
    """
    Устанавливает типовые значения, используемые для отправления сообщений.
    """

    COMMON = {
        'access_denied': 'Доступ запрещен. Сорри',
        'reduce_frequency': 'сорри! Одна команда в 12 сек или после ответа на предыдущую',  # noqa
        'all_busy': 'сорри, все заняты.',
        'wipe': 'У меня не получилось проверить аккаунты :( сорри',  # noqa
    }

    BEGINNINGS = {
        'normal': 'Трайни эти ',
        'trouble': 'Проблемы с аккаунтами: ',
        'lost_data': 'Есть потерянные аккаунты! Проверены: ',
        'trouble_ui': '. У меня не получилось в эти, можешь попробовать вручную: ',
    }

    ACCOUNT_TYPES = {
        'general': 'общие: ',
        'regional': 'региональные: ',
    }

    DEFAULT_CHAT = 000000000
