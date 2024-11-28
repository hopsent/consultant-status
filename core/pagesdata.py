class PagesData:
    """
    Определяет константы, используемые программой.
    В частности, определяет дефолтное значение URL,
    наименования полей, а также наименования и CSS кнопок
    и попапа, которые используются драйвером на сайте.
    """

    DEFAULT_URL: str = 'https://www.google.com'

    FORM_FIELDS: dict = {
        'login': '#loginform-login',
        'password': '#loginform-password',
    }

    BUTTONS: dict = {
        'sign_in': '#buttonLogin',
        'search': '.x-page-components-main-toolbar__left-buttons > a:nth-child(2)',  # CSS +
        'account_info_button': 'div.x-page-components-main-toolbar-top__button:nth-child(6)',
        'change_personality': 'tr.x-menu__content-row:nth-child(6) > td:nth-child(2) > div:nth-child(1)',  # noqa
        'welcome_button': 'body > div.popupFrameContainer > div > div > div > div > div > button',
        'straight_exit': 'div.x-page-components-main-toolbar-top__button:nth-child(7)',
    }

    TEXT_TITLES: dict = {
        'start_page': 'Учетная запись занята.',
        'search_page': 'Как искать:',
    }
