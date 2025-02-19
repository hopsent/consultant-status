class PagesData:
    """
    Определяет константы, используемые программой.
    В частности, определяет дефолтное значение URL,
    CSS полей, кнопок, тексты атрибутов элементов,
    которые используются драйвером на сайте.
    """

    DEFAULT_URL: str = 'https://www.google.com'

    FORM_FIELDS: dict = {
        'login': '#loginform-login',
        'password': '#loginform-password',
    }

    BUTTONS: dict = {
        'sign_in': '#buttonLogin',
        'search': '.x-page-components-main-toolbar__left-buttons > a:nth-child(2)',  # noqa
        'straight_exit': 'div.x-page-components-main-toolbar-top__button:nth-child(7)',  # noqa
        'no_longer_busy': '.x-toast__close',
    }

    TEXTS: dict = {
        'data_title': 'Выйти из системы и освободить учетную запись.',
    }

    MISC: dict = {
        'popup_busy': '.popupFrameContainer',
        'popup_busy_class': 'popupFrameContainer',
    }
