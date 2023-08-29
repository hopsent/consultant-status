class PagesData:
    """
    Определяет константы, используемые программой.
    В частности, определяет дефолтное значение URL,
    наименования полей, а также наименования и CSS кнопок
    и попапа, которые используются драйвером на сайте.
    """

    DEFAULT_URL: str = 'https://www.google.com/'
    DEFAULT_URL_CHECKER: str = 'https://www.wikipedia.org/'

    FORM_FIELDS: dict = {
        'login': 'loginform-login',
        'password': 'loginform-password',
        'error': '.form__error',  # CSS-селектор
    }

    BUTTONS: dict = {
        'sign_in': 'buttonLogin',
        'retry_button': '.modal__body > p:nth-child(4) > a:nth-child(1)',
        'welcome_button': 'button.x-button:nth-child(1)',
        # Не используется сейчас.
        'change_profile_not_now': '.popupButtons > button:nth-child(2)',
        'search': '.mainToolbar > a:nth-child(5) > button:nth-child(1)',
        'logout': 'logout',
        'confirm_logout': 'button.x-button:nth-child(1)',
        'account_busy_leave': 'div.popupContent:nth-child(3) > div:nth-child(2) > button:nth-child(2)', # noqa
    }

    POPUP: dict = {
        'auth_error_popup': 'asyncLoginModalError',  # Не используется сейчас.
        'welcome_popup': '.popupOverlay',
    }

    PROFILE_STATUS: dict = {
        'info': '.link > span:nth-child(1)',
        'default_status': 'Юрист',
    }

    TEXT_TITLES: dict = {
        'start_page': 'Выйти из системы',
        'search_page': 'Быстрый поиск'
    }

    LABEL: dict = {
        'search': '.label > span:nth-child(1)',
    }
