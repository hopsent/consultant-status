import logging
from logging.handlers import RotatingFileHandler
from os import getenv
from typing import Optional

from dotenv import load_dotenv
from selenium.common.exceptions import (TimeoutException,
                                        ElementClickInterceptedException,
                                        NoSuchElementException)
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

import core.exceptions as EXC
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

    def check_account_is_busy(self, driver: Firefox) -> object:
        """
        Проверка на то, занят ли аккаунт.
        После успешного логина на сайт, нажимается кнопка "Найти".
        В обычном случае нажатие на кнопку позволяет перейти к
        поиску документов. Если аккаунт занят, сайт показывает поп-ап.
        """

        login = self.login
        password = self.password
        URL = self.URL
        # Общая информация.
        message = f'Аккаунт {login}.\n'

        # Проверки корректного нахождения на целевом URL.
        if driver.current_url == PD.DEFAULT_URL:
            message_er_url = (
                message + 'При выполнении метода check_account_is_busy драйвер'
                'находился на дефолтном URL.'
            )
            driver.get(getenv('URL', default=PD.DEFAULT_URL_CHECKER))
            if URL[-14:-4] not in driver.current_url:
                message_er_url += (
                    'Проблема не решена. Вероятно, проблема с .env.'
                    f' Текущий URL: {driver.current_url}'
                )
                logger.error(message_er_url, exc_info=True)
                return self
            message_er_url += f' Решено. Текущий URL: {driver.current_url}'
            logger.error(message_er_url, exc_info=True)

        if not driver.current_url == URL:
            if URL[-14:-4] not in driver.current_url:
                message_er_url = (
                    message + 'При выполнении метода'
                    ' check_account_is_busy достичь целевого URL не удалось.'
                    f' Текущий URL: {driver.current_url}'
                )
                logger.error(message_er_url, exc_info=True)
                return self
            driver.get(PD.DEFAULT_URL)
            driver.get(URL)

        try:  # Логинимся.
            driver.find_element(
                value=PD.FORM_FIELDS['login']
            ).send_keys(login)
            driver.find_element(
                value=PD.FORM_FIELDS['password']
            ).send_keys(password)
            driver.find_element(value=PD.BUTTONS['sign_in']).click()
        except ElementClickInterceptedException:
            logger.error(message, exc_info=True)
            try:
                ActionChains(driver).send_keys(Keys.ESCAPE).perform()
                driver.find_element(
                    value=PD.FORM_FIELDS['login']
                ).send_keys(login)
                driver.find_element(
                    value=PD.FORM_FIELDS['password']
                ).send_keys(password)
                driver.find_element(value=PD.BUTTONS['sign_in']).click()
            except EXC.CannotLogInProperly:
                logger.error(message, exc_info=True)
                driver.get(URL)
                return self
        except EXC.CannotLogInProperly:
            logger.error(message, exc_info=True)
            driver.get(URL)
            return self

        # В результате логина изменяется содержимое страницы. Ожидаем.
        wait = WebDriverWait(driver, 5)
        search_css = By.CSS_SELECTOR, PD.BUTTONS['search']
        try:
            wait.until(EC.presence_of_element_located(search_css))
        except TimeoutException:
            if driver.current_url == URL:
                ActionChains(driver).send_keys(Keys.ESCAPE).perform()
                logger.error(message, exc_info=True)
                try:
                    driver.find_element(
                        value=PD.FORM_FIELDS['login']
                    ).send_keys(login)
                    driver.find_element(
                        value=PD.FORM_FIELDS['password']
                    ).send_keys(password)
                    driver.find_element(value=PD.BUTTONS['sign_in']).click()
                except TimeoutException or NoSuchElementException:
                    logger.error(message, exc_info=True)
                    driver.get(URL)
                    return self

        # Справляемся с приветственным поп-ап: ждем поп-ап,
        # нажимаем на кнопку Esc, когда он появится.
        welcome_button = By.CSS_SELECTOR, PD.BUTTONS['welcome_button']
        wait = WebDriverWait(driver, 3)
        try:
            wait.until(EC.visibility_of_element_located(welcome_button))
        except TimeoutException:
            msg_wlc_er = message + 'Не подгрузилась кнопка приветствия'
            logger.info(msg_wlc_er, exc_info=True)
        finally:
            ActionChains(driver).send_keys(Keys.ESCAPE).perform()

        # Нажимаем на кнопку "Быстрый поиск", пробуя, тем самым,
        # пройти на экран, который недоступен, только если аккаунт занят.
        # Также запоминаем URL, чтобы организовать ожидание при его смене,
        # немного замедлив работу драйвера.
        # Нажатие на Esc уменьшает риск незапланированного поп-апа.
        url_before_search = str(driver.current_url)
        try:
            ActionChains(driver).send_keys(Keys.ESCAPE).perform()
            driver.find_element(*search_css).click()
        except ElementClickInterceptedException:
            ActionChains(driver).send_keys(Keys.ESCAPE).perform()
            try:
                driver.find_element(*search_css).click()
                message_acc_profile = (
                    message + 'Нажатию на "Поиск" помешал попап. Решено.'
                )
                logger.info(message_acc_profile, exc_info=True)
            except (
                ElementClickInterceptedException or NoSuchElementException
            ):
                logger.error(message, exc_info=True)
                driver.get(URL)
                return self
        except NoSuchElementException:
            logger.error(message, exc_info=True)
            driver.get(URL)
            return self

        # Ожидаем, когда изменится URL, замедляя браузер.
        try:
            wait.until(EC.url_changes(url_before_search))
        except TimeoutException:
            logger.error(message, exc_info=True)
            ActionChains(driver).send_keys(Keys.ESCAPE).perform()
            driver.find_element(*search_css).click()

        # Ищем элементы, отображающиеся на странице поиска либо на
        # главной странице, когда нажатие на "Поиск" приводит
        # к поп-апу - аккаунт занят. Вебдрайвер ждет,
        # пока один из двух уникальных элементов не обнаружится.
        wait = WebDriverWait(driver, 5)
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
            if actual_element.text[:2] == PD.TEXT_TITLES['search_page'][:2]:
                self.is_busy = False
        except TimeoutException:
            logger.error(message, exc_info=True)
            driver.get(URL)
            return self

        # Тактика выхода одинаковая для любого статуса аккаунта:
        # нажимаем на Esc, чтобы закрыть любые всплывшие окна,
        # нажимаем на кнопку выхода и нажимаем на всплывшую
        # кнопку подтверждения выхода.
        try:
            ActionChains(driver).send_keys(Keys.ESCAPE).perform()
            driver.find_element(value=PD.BUTTONS['logout']).click()
            driver.find_element(
                by=By.CSS_SELECTOR,
                value=PD.BUTTONS['confirm_logout']
            ).click()
        except (
            ElementClickInterceptedException or NoSuchElementException
        ):  # Проводим выход дважды, т.к. часто появляется поп-ап.
            logger.error(message, exc_info=True)
            try:
                ActionChains(driver).send_keys(Keys.ESCAPE).perform()
                driver.find_element(value=PD.BUTTONS['logout']).click()
                driver.find_element(
                    by=By.CSS_SELECTOR,
                    value=PD.BUTTONS['confirm_logout']
                ).click()
            except (
                ElementClickInterceptedException or NoSuchElementException
            ):
                logger.error(message, exc_info=True)
                driver.get(PD.DEFAULT_URL)
                driver.get(URL)

        return self

    def __str__(self) -> str:

        # Использование последних трех цифр делает название
        # аккаунта человекочитаемым, как это принято у ЦА.
        return self.login[-3:]

    def __repr__(self) -> str:

        return self.login[-3:]
