from os import getenv
from typing import Optional, List, Union
from multiprocessing import Process, Queue

from dotenv import load_dotenv
from keyring import get_credential
from keyring.credentials import SimpleCredential, Credential
from selenium.webdriver import Firefox

from core.account import Account


load_dotenv()


class MultiCheckHandler:
    """
    Абстрактный класс, служащий для целей совмещения инстансов
    Account и DriversHandler - для организации мультипоточности
    с помощью библиотеки multiprocessing и инстансов Process.

    Позволяет проверить сразу несколько Account на предмет
    текущего статуса на целевом сайте.
    
    Параметры regional и amount - составная часть бизнес-логики.
    Инстанцируя объект данного класса, необходимо указать, в какую
    часть бизнес-логики встроен объект, то есть какую группу аккаунтов
    ему необходимо будет обслуживать. Данное указание делается объектом
    презентера, которому неизвестны точные параметры бизнес-логики, поэтому
    установлены константы, зависящие от содержания .env-файла.
    """

    REGIONAL_AMOUNT: int = int(getenv('REGIONAL_AMOUNT', default=0))
    GENERAL_AMOUNT: int = int(getenv('GENERAL_AMOUNT', default=0))

    REGIONAL_PREFIX: str = getenv('REGIONAL_PREFIX', default='')
    GENERAL_PREFIX: str = getenv('GENERAL_PREFIX', default='')

    def __init__(self,
                 regional: bool,
                 amount: Optional[int] = None
                 ) -> None:

        self.regional = regional
        if self.regional is True:
            self.amount = self.REGIONAL_AMOUNT
        else:
            self.amount = self.GENERAL_AMOUNT

    def create_accounts_data_list(self) -> List[Union[Credential, None]]:  # Property - _
        """
        Получаем из хранилища keyring чувствительную информацию
        от аккаунтов на целевом сайте. Возвращаем список объектов
        SimpleCredential. Этот метод необходимо, чтобы составить
        список Account'ов для участия в мультипроцессинговой функции.
        """

        if self.amount == 0:  # Проверка корректности работы .env-файла.
            pass

        # Этот блок кода обусловлен способом хранения данных
        # если требуется проверка региональных аккаунтов - выбирается
        # слово, соответствующее префиксу хранения данных.
        if self.regional is True:
            prefix = self.REGIONAL_PREFIX
        else:
            prefix = self.GENERAL_PREFIX
        if len(prefix) == 0:  # Проверка работоспособности .env-файла.
            pass

        # Предоставляем заранее сохраненные с использованием keyring данные.
        return [get_credential(f'{prefix}{i}', None) for i in range(self.amount)]

    def create_and_check_account(self,
                                account_data: SimpleCredential,
                                driver: Firefox,
                                q: Queue) -> None:
        """
        Из объектов SimpleCredential извлекаются логин и пароль
        и создаётся объект Account. На таком объекте Account
        вызывается метод acheck_account_is_busy.
        Тем самым проверяется статус активности аккаунта.
        Окончание выполнения метода (объекты Account) включаются
        в очередь q. Является целью каждого процесса Process,
        то есть используется как целевая исполняемая функция
        при мультипроцессинговости.
        """

        login = account_data.username
        password = account_data.password
        account = Account(login=login, password=password)
        status = account.check_account_is_busy(driver)
        q.put_nowait(status)
    
    def processing(self, drivers: list) -> Queue:
        """
        Разбивает исполнение программы на процессы, чтобы,
        преодолев GIL, одновременно исследовался статус
        активности нескольких аккаунтов на сайте.
        Возвращает очередь q из объектов Account с учетом
        результатов выполнения метода - target_process_function,
        проверяющего статус активности одного аккаунта.
        """

        accounts_data = self.create_accounts_data_list()

        processes = []
        q = Queue()

        for i in range(self.amount):
            p = Process(
                target=self.create_and_check_account,
                args=(accounts_data[i], drivers[i], q)
            )
            processes.append(p)
            p.start()

        [p.join() for p in processes]

        return q
