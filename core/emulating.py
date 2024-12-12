import logging
from logging.handlers import RotatingFileHandler
from os import getenv
from time import sleep
from typing import Literal, Tuple

from dotenv import load_dotenv
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

from core.pagesdata import PagesData as PD
from core.account import Account


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


class Emulator:
    """
    Имитирует поведение человека на заданном сайте, чтобы получить
    данные о том, занят аккаунт или свободен.

    Свойства:
    driver - объект Firefox(), на котором будем эмулировать поведение
    человека на сайте;
    account - объект Account() с заданными свойствами login,
    password и is_busy (последнее по умолчанию - None).
    """

    URL = getenv('URL', default=PD.DEFAULT_URL)

    def __init__(self, driver: Firefox, account: Account) -> None:
        self.driver = driver
        self.account = account

    def fill_in_field(self,
                      css: Tuple[Literal['css selector'], str],
                      wait: WebDriverWait,
                      creds: str) -> None:
        """
        Чистим поле на стартовой странице. Заполняем поле.
        Функция получает:
        css - сведения о поле на сайте, которое нужно очистить
        и заполнить;
        wait - объект WebDriverWait;
        creds - строка с информацией, вносимой в заданное поле.
        """

        field = wait.until(EC.element_to_be_clickable(css))
        if len(field.text) != 0:
            field.click()
            field.send_keys(Keys.CONTROL + 'a')
            field.send_keys(Keys.DELETE)
        field.send_keys(creds)

    def login_to_site(self, wait: WebDriverWait) -> None:
        """
        Логинимся на целевой сайт.
        """

        login_field = By.CSS_SELECTOR, PD.FORM_FIELDS['login']
        password_field = By.CSS_SELECTOR, PD.FORM_FIELDS['password']
        button_sign_in = By.CSS_SELECTOR, PD.BUTTONS['sign_in']

        ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()
        self.fill_in_field(password_field, wait, self.account.password)
        self.fill_in_field(login_field, wait, self.account.login)
        ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()
        wait.until(EC.element_to_be_clickable(button_sign_in)).click()

    def check_account_is_busy(self) -> Account:
        """
        Проверка на то, занят ли аккаунт.
        В зависимости от результата устанавливает свойство объекта
        Account() is_busy: True, False или оставляет None.
        Возвращает объект Account().
        """
        c_url = self.driver.current_url
        wait = WebDriverWait(self.driver, 6)
        message = f'Аккаунт {self.account.login}. URL {c_url}\n'

        # Проверяем нахождение на целевом URL.
        if ('consultant' not in c_url) or ('end&start' in c_url):
            try:
                self.driver.get(self.URL)
                self.login_to_site(wait)
                sleep(6)
            except Exception:
                logger.error(message, exc_info=True)

        try:
            ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()
            search_css = By.CSS_SELECTOR, PD.BUTTONS['search']
            wait.until(EC.element_to_be_clickable(search_css)).click()

            ac_elem = wait.until(
                EC.any_of(
                    EC.presence_of_element_located(
                        (By.XPATH, f'//p[text()="{PD.TEXTS["start_page"]}"]')
                    ),
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, PD.BUTTONS['straight_exit'])
                    )
                )
            )

            if ac_elem.text == PD.TEXTS['start_page']:
                self.account.is_busy = True
                ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()
            elif ac_elem.get_attribute('data-title') == PD.TEXTS['data_title']:
                self.account.is_busy = False
                ac_elem.click()
                wait.until(EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, PD.BUTTONS['no_longer_busy'])
                )).click()

        except Exception:
            logger.error(message, exc_info=True)

        return self.account
