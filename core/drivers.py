from os import getenv

from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service

from core.pagesdata import PagesData as PD
from core.exceptions import ENVFileException


load_dotenv()


class DriversHandler:
    """
    Класс предназначен для управления несколькими группами
    драйверов в зависимости от количества, которое будет известно
    заранее.
    """

    EXEC_PATH: str = getenv('EXEC_PATH', default='geckodriver')
    URL: str = getenv('URL', default=PD.DEFAULT_URL)
    LOG_PATH: str = 'logs/geckodriver.log'
    REGIONAL_AMOUNT: int = int(getenv('REGIONAL_AMOUNT', default=0))
    GENERAL_AMOUNT: int = int(getenv('GENERAL_AMOUNT', default=0))
    TOTAL_AMOUNT: int = max(REGIONAL_AMOUNT, GENERAL_AMOUNT)

    def __init__(self, drivers=[]) -> None:
        self.drivers = drivers

    def create_drivers(self) -> None:
        """
        Создаём драйвера Файрфокс на основе гецкодрайвера.
        Headless режим активирован. Каждый драйвер заблаговременно
        размещается на искомом URL - тем самым ускоряется работа
        основного алгоритма при первом запуске. Формируется
        и возвращается список драйверов.
        """

        if self.TOTAL_AMOUNT == 0:
            raise ENVFileException(
                'При создании списка драйверов обнаружены дефолтные значения'
                f'переменных: количество аккаунтов - {self.TOTAL_AMOUNT}.'
            )

        for _ in range(self.TOTAL_AMOUNT):
            options = Options()
            options.headless = True
            options = options
            service = Service(
                executable_path=self.EXEC_PATH,
                log_path=self.LOG_PATH
            )
            driver = webdriver.Firefox(service=service, options=options)
            driver.get(self.URL)
            self.drivers.append(driver)
