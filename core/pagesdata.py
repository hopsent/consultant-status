class PagesData:
    """
    Определяет константы, используемые программой.
    В частности, определяет дефолтное значение URL,
    наименования полей, а также наименования и CSS кнопок
    и попапа, которые используются драйвером на сайте.
    """

    DEFAULT_URL: str = 'https://www.google.com/'

    FORM_FIELDS: dict = {
        'login': 'loginform-login',  # ID.
        'password': 'loginform-password',  # ID.
    }

    BUTTONS: dict = {
        'sign_in': 'buttonLogin',  # ID.
        'search': '.x-main-toolbar__left-buttons > a:nth-child(2)',  # CSS
        'logout': 'div.x-main-toolbar-top__button:nth-child(7)',  # CSS
        'welcome_button': 'button.x-button:nth-child(1)',  # CSS
        'account_busy_leave': '.popupButtons > button:nth-child(2)',
        'account_info_button': 'div.x-main-toolbar-top__button:nth-child(6)',
        'change_personality': 'tr.x-menu__content-row:nth-child(6) > td:nth-child(2) > div:nth-child(1)',  # noqa
    }

    TEXT_TITLES: dict = {
        'start_page': 'Выйти из системы',
        'search_page': 'Быстрый поиск'
    }

    LABEL: dict = {
        'search': '.x-page-search-plus-panel__title-text',
    }
