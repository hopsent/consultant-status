from typing import Optional


class Account:
    """
    Аккаунт состоит из параметров логина login,
    пароля password и состояния активности на сайте
    is_busy. Последний параметр вычисляется методом
    Emulator().check_account_is_busy() и по умолчанию - None.
    """

    def __init__(self,
                 login: str,
                 password: str,
                 is_busy: Optional[bool] = None
                 ) -> None:

        self.login = login
        self.password = password
        self.is_busy = is_busy

    def __str__(self) -> str:

        # Использование последних трех цифр делает название
        # аккаунта человекочитаемым, как это принято у ЦА.
        return self.login[-3:]

    def __repr__(self) -> str:

        return self.login[-3:]
