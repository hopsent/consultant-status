from typing import List
from os import getenv

from dotenv import load_dotenv
from keyring import get_credential
from keyring.credentials import SimpleCredential


load_dotenv()


class DataExtractor:
    """
    Этот класс нужен, чтобы получить из памяти машины
    предзагруженные сведения о логинах и паролях аккаунтов.
    """

    REGIONAL_AMOUNT: int = int(getenv('REGIONAL_AMOUNT', default=0))
    GENERAL_AMOUNT: int = int(getenv('GENERAL_AMOUNT', default=0))
    REGIONAL_PREFIX: str = getenv('REGIONAL_PREFIX', default='')
    GENERAL_PREFIX: str = getenv('GENERAL_PREFIX', default='')

    def __init__(self, regional: bool) -> None:
        self.regional = regional

    def get_account_data(self) -> List[SimpleCredential]:
        """
        Получаем из хранилища keyring чувствительную информацию
        от аккаунтов на целевом сайте. Возвращаем список объектов
        SimpleCredential.
        """

        prefix = self.GENERAL_PREFIX
        amount = self.GENERAL_AMOUNT
        if self.regional:
            prefix = self.REGIONAL_PREFIX
            amount = self.REGIONAL_AMOUNT

        credentials = []

        for i in range(amount):
            credential = get_credential(f'{prefix}{i}', None)
            if credential is not None:
                credentials.append(credential)
            else:
                raise Exception(f'Нет инфо об аккаунте: {prefix}{i}')

        return credentials
