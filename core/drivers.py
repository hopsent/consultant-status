from os import getenv

from dotenv import load_dotenv
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service


load_dotenv()


class DriverHandler:
    """
    Класс предназначен для управления несколькими группами
    драйверов в зависимости от количества, которое будет известно
    заранее.
    """

    EXEC_PATH: str = getenv('EXEC_PATH', default='geckodriver')
    LOG_PATH: str = 'logs/geckodriver.log'

    def __init__(self) -> None:
        pass

    def create_driver(self) -> Firefox:
        """
        Создаём драйвер Файрфокс на основе гецкодрайвера.
        Headless режим активирован.
        """

        options = Options()
        options.headless = True
        options = options
        service = Service(
            executable_path=self.EXEC_PATH,
            log_path=self.LOG_PATH
        )
        return Firefox(service=service, options=options)
