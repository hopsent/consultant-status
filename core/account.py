import logging
from logging.handlers import RotatingFileHandler
from os import getenv
from typing import Optional
from time import sleep

from dotenv import load_dotenv
from selenium.common.exceptions import (TimeoutException,
                                        ElementClickInterceptedException)
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

from core.pagesdata import PagesData as PD


load_dotenv()

secret_token = getenv('TOKEN', default='0')
port = getenv('PORT', default='8443')
ip = getenv('SERVER_ADDRESS', default='0.0.0.0')


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
    об элементах веб-страницы в HTTP-response, перечисленных
    в модуле pagesdata при эмуляции браузером Firefox
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

    def login_to_site(self, driver: Firefox, wait: WebDriverWait) -> object:

        message = f'Аккаунт {self.login}. URL {driver.current_url}\n'
        login_field = By.ID, PD.FORM_FIELDS['login']
        password_field = By.ID, PD.FORM_FIELDS['password']
        button_sign_in = By.ID, PD.BUTTONS['sign_in']

        try:  # Заполняем форму логина.
            wait.until(EC.element_to_be_clickable(password_field))
            wait.until(EC.element_to_be_clickable(login_field))
            driver.find_element(*login_field).clear()
            driver.find_element(*password_field).clear()
            driver.find_element(*login_field).send_keys(self.login)
            driver.find_element(*password_field).send_keys(self.password)
            wait.until(EC.element_to_be_clickable(button_sign_in))
            driver.find_element(*button_sign_in).click()
        except Exception:
            logger.error(message, exc_info=True)
            driver.get(self.URL)
            return self

    def leave_account(self, driver: Firefox, wait: WebDriverWait) -> None:
        """
        Общий алгоритм выхода из аккаунта: нажимаются две отведенные для
        этого на сайте кнопки. Esc добавлена для исключения поп-апа.
        """
        ActionChains(driver).send_keys(Keys.ESCAPE).perform()
        wait.until(EC.element_to_be_clickable(
                (By.CSS_SELECTOR, PD.BUTTONS['account_info_button']))
        ).click()
        wait.until(EC.element_to_be_clickable(
                (By.CSS_SELECTOR, PD.BUTTONS['change_personality']))
        ).click()

    def check_account_is_busy(self, driver: Firefox) -> object:
        """
        Проверка на то, занят ли аккаунт.
        После успешного логина на сайт, нажимается кнопка "Найти".
        В обычном случае нажатие на кнопку позволяет перейти к
        поиску документов. Если аккаунт занят, сайт показывает поп-ап.
        """

        URL = self.URL
        MARK = 'login.'
        wait = WebDriverWait(driver, 7)

        # Общая информация.
        message = f'Аккаунт {self.login}. URL {driver.current_url}\n'

        # Проверяем нахождение на целевом URL. Решаем вопрос.
        if MARK not in driver.current_url:
            if driver.current_url != PD.DEFAULT_URL:
                try:
                    driver.get(PD.DEFAULT_URL)
                    sleep(1)
                    driver.get(URL)
                except Exception:
                    logger.error(message, exc_info=True)
                    return self
            elif driver.current_url == PD.DEFAULT_URL:
                try:
                    driver.get(URL)
                    sleep(2)
                except Exception:
                    logger.error(message, exc_info=True)
                    return self
            else:
                logger.error(message, exc_info=True)
                driver.get(PD.DEFAULT_URL)
                driver.get(URL)
                return self

        # Логинимся.
        self.login_to_site(driver, wait)

        # Проверяем, подгружается ли сайт.
        try:
            wait.until(EC.url_changes(URL))
        except Exception:
            logger.error(message, exc_info=True)
            driver.get(PD.DEFAULT_URL)
            driver.get(URL)
            return self

        # Справляемся с приветственным поп-ап: ждем поп-ап,
        # нажимаем на кнопку Esc, когда он появится.
        welcome_button = By.CSS_SELECTOR, PD.BUTTONS['welcome_button']
        try:
            wait.until(EC.visibility_of_element_located(welcome_button))
        except TimeoutException:
            msg_wlc_er = message + 'Не подгрузилась кнопка приветствия'
            logger.info(msg_wlc_er, exc_info=True)
            if URL == driver.current_url:
                self.login_to_site(driver, wait)
        finally:
            ActionChains(driver).send_keys(Keys.ESCAPE).perform()

        # Нажимаем на кнопку "Быстрый поиск", пробуя, тем самым,
        # пройти на экран, который недоступен, только если аккаунт занят.
        # Нажатие на Esc уменьшает риск незапланированного поп-апа.
        search_css = By.CSS_SELECTOR, PD.BUTTONS['search']
        ActionChains(driver).send_keys(Keys.ESCAPE).perform()
        try:
            ActionChains(driver).send_keys(Keys.ESCAPE).perform()
            wait.until(EC.element_to_be_clickable(search_css)).click()
        except ElementClickInterceptedException:
            try:
                ActionChains(driver).send_keys(Keys.ESCAPE).perform()
                wait.until(EC.element_to_be_clickable(search_css)).click()
                message_acc_profile = (
                    message + 'Нажатию на "Поиск" что-то помешало. Решено.'
                )
                logger.info(message_acc_profile, exc_info=True)
            except Exception:
                logger.error(message, exc_info=True)
                driver.get(PD.DEFAULT_URL)
                driver.get(URL)
                return self
        except Exception:
            logger.error(message, exc_info=True)
            driver.get(PD.DEFAULT_URL)
            driver.get(URL)
            return self

        # Ищем элементы, отображающиеся на странице поиска либо на
        # главной странице, когда нажатие на "Поиск" приводит
        # к поп-апу - аккаунт занят. Вебдрайвер ждет,
        # пока один из двух уникальных элементов не обнаружится.
        start_page_element = EC.presence_of_element_located(
            (By.CSS_SELECTOR, PD.BUTTONS['account_busy_leave'])
        )
        search_page_element = EC.presence_of_element_located(
            (By.CSS_SELECTOR, PD.LABEL['search'])
        )
        actual_element = wait.until(
            EC.any_of(start_page_element, search_page_element)
        )

        # Определяем текст уникальных элементов и сравниваем с референтным
        # значением уникального элемента стартовой страницы и уникального
        # элемента страницы поиска по первым трём буквам.
        try:
            if actual_element.text[:2] == PD.TEXT_TITLES['start_page'][:2]:
                self.is_busy = True
            elif actual_element.text[:2] == PD.TEXT_TITLES['search_page'][:2]:
                self.is_busy = False
            ActionChains(driver).send_keys(Keys.ESCAPE).perform()
        except Exception:
            logger.error(message, exc_info=True)
            driver.get(PD.DEFAULT_URL)
            driver.get(URL)
            return self

        # Тактика выхода одинаковая для любого статуса аккаунта:
        # нажимаем на Esc, чтобы закрыть любые всплывшие окна,
        # нажимаем на кнопку выхода и нажимаем на всплывшую
        # кнопку подтверждения выхода.
        try:
            self.leave_account(driver, wait)
        # Проводим выход дважды, т.к. часто появляется поп-ап.
        except ElementClickInterceptedException:
            logger.error(message, exc_info=True)
            try:
                self.leave_account(driver, wait)
            except Exception:
                logger.error(message, exc_info=True)
                driver.get(PD.DEFAULT_URL)
                driver.get(URL)
                return self
        except Exception:
            logger.error(message, exc_info=True)
            driver.get(PD.DEFAULT_URL)
            driver.get(URL)
            return self

        return self

    def __str__(self) -> str:

        # Использование последних трех цифр делает название
        # аккаунта человекочитаемым, как это принято у ЦА.
        return self.login[-3:]

    def __repr__(self) -> str:

        return self.login[-3:]
