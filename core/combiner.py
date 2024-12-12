from core.account import Account
from core.emulating import Emulator
from core.extractor import DataExtractor
from core.drivers import DriverHandler


class Combiner:
    """
    Создаёт окна браузера Файрфокс, готовые к работе.
    """

    def __init__(self, regional) -> None:
        self.regional = regional

    def combine_driver_with_account(self):
        data = DataExtractor(regional=self.regional).get_account_data()
        accounts = [
            Account(login=d.username, password=d.password) for d in data
        ]
        dh = DriverHandler()
        return [Emulator(dh.create_driver(), acc) for acc in accounts]
