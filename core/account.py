import logging
from logging.handlers import RotatingFileHandler
from os import getenv
from typing import Optional
from time import sleep

from dotenv import load_dotenv
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement

from core.pagesdata import PagesData as PD


load_dotenv()

formater = logging.Formatter(
    '%(asctime)s, %(levelname)s, %(process)d, %(message)s, %(name)s'
)
handler = RotatingFileHandler(
    'logs/' + __name__ + '.log',
    maxBytes=52428800,
)
handler.setFormatter(formater)
handler.setLevel(logging.NOTSET)

logger = logging.getLogger(__name__)
logger.setLevel(logging.NOTSET)
logger.addHandler(handler)


class Account:
    """
    Предназначен для управления информацией
    о состоянии конкретного аккаунта на сайте.

    Аккаунт состоит из параметров логина login,
    пароля password и состояния активности на сайте
    is_busy. Последний параметр вычисляется методом
    check_account_is_busy() и по умолчанию - None.

    Указанный метод является основным и использует данные
    об элементах веб-страницы при эмуляции браузером Firefox
    поведения человека на заданном сайте.
    """

    URL = getenv('URL', default=PD.DEFAULT_URL)

    def __init__(self,
                 login: str,
                 password: str,
                 is_busy: Optional[bool] = None
                 ) -> None:

        self.login = login
        self.password = password
        self.is_busy = is_busy

    def leave_account(self, driver: Firefox, wait: WebDriverWait, msg: str) -> object:
        """
        Общий алгоритм выхода из аккаунта: нажимаются две отведенные для
        этого на сайте кнопки. Esc добавлена для исключения поп-апа.
        """

        ActionChains(driver).send_keys(Keys.ESCAPE).perform()
        try:
            wait.until(EC.element_to_be_clickable(
                (By.CSS_SELECTOR, PD.BUTTONS['straight_exit']))
            ).click()
            wait.until(EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, PD.BUTTONS['account_info_button']))
            ).click()
            wait.until(EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, PD.BUTTONS['change_personality']))
            ).click()
        except Exception:
            logger.error(msg, exc_info=True)
            driver.get(PD.DEFAULT_URL)
            return self

    def emptyfier(self, field: WebElement) -> None:
        """
        Чистим формы на стартовой странице.
        """

        if len(field.text) != 0:
            field.click()
            field.send_keys(Keys.CONTROL + 'a')
            field.send_keys(Keys.DELETE)

    def login_to_site(self, wait: WebDriverWait) -> None:
        """
        Логинимся.
        """

        login_field = By.CSS_SELECTOR, PD.FORM_FIELDS['login']
        password_field = By.CSS_SELECTOR, PD.FORM_FIELDS['password']
        button_sign_in = By.CSS_SELECTOR, PD.BUTTONS['sign_in']

        password_field = wait.until(EC.element_to_be_clickable(password_field))
        self.emptyfier(password_field)
        password_field.send_keys(self.password)
        login_field = wait.until(EC.element_to_be_clickable(login_field))
        self.emptyfier(login_field)
        login_field.send_keys(self.login)
        wait.until(EC.element_to_be_clickable(button_sign_in)).click()

    def push_search_button(self, driver: Firefox, wait: WebDriverWait) -> None:
        """
        Нажимаем на кнопку "Быстрый поиск", пробуя, тем самым, пройти на экран,
        который доступен, только если аккаунт не занят.
        Нажатие на Esc уменьшает риск незапланированного поп-апа.
        """

        if self.login[-2:] in '14' or self.login[-2:] in '15':
            welcome_button = By.CSS_SELECTOR, PD.BUTTONS['welcome_button']
            try:
                wait.until(EC.visibility_of_element_located(welcome_button))
            except Exception:
                message = self.login + '. Не подгрузилась кнопка приветствия'
                logger.info(message, exc_info=True)
            finally:
                ActionChains(driver).send_keys(Keys.ESCAPE).perform()
        else:
            sleep(3)
        search_css = By.CSS_SELECTOR, PD.BUTTONS['search']
        ActionChains(driver).send_keys(Keys.ESCAPE).perform()
        wait.until(EC.element_to_be_clickable(search_css)).click()

    def check_availability(self, wait: WebDriverWait) -> None:
        """
        Определяем текст уникальных элементов и сравниваем с референтным
        значением уникального элемента стартовой страницы и уникального
        элемента страницы поиска
        """

        busy_element = EC.presence_of_element_located(
            (By.XPATH, f'//p[text()="{PD.TEXT_TITLES["start_page"]}"]')
        )
        spare_element = EC.presence_of_element_located(
            (By.XPATH, f'//b[text()="{PD.TEXT_TITLES["search_page"]}"]')
        )
        actual_element = wait.until(EC.any_of(busy_element, spare_element))
        if actual_element.text == PD.TEXT_TITLES['start_page']:
            self.is_busy = True
        elif actual_element.text == PD.TEXT_TITLES['search_page']:
            self.is_busy = False

    def check_account_is_busy(self, driver: Firefox) -> object:
        """
        Проверка на то, занят ли аккаунт.
        """

        wait = WebDriverWait(driver, 6)
        message = f'Аккаунт {self.login}. URL {driver.current_url}\n'

        # Проверяем нахождение на целевом URL.
        if not 'login.' in driver.current_url:
            try:
                driver.get(self.URL)
                sleep(2)
            except Exception:
                logger.error(message, exc_info=True)
                return self

        try:
            self.login_to_site(wait)
            self.push_search_button(driver, wait)
            self.check_availability(wait)
        except Exception:
            logger.error(message, exc_info=True)

        self.leave_account(driver, wait, message)
        return self

    def __str__(self) -> str:

        # Использование последних трех цифр делает название
        # аккаунта человекочитаемым, как это принято у ЦА.
        return self.login[-3:]

    def __repr__(self) -> str:

        return self.login[-3:]
