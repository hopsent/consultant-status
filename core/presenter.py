from multiprocessing import Queue
from typing import Dict

from core.drainer import Drainer
from core.status import Status as ST


class Presenter:
    """
    Этот класс нужен, чтобы получить входные данные и
    на их основе извлечь информацию из методов,
    запущенных объекте MultiCheckHandler .
    """

    def composing(self, q: Queue) -> Dict:
        """
        Объект q создан методом интерфейса MultiCheckHandler.
        С помощью интерфейса Drainer создаём словарь
        с объектами Account. Ключи словаря соответствуют
        статусу объектов Account на целевом сайте.

        После экстрактирования статуса обнуляем его.
        """

        sort_account_to_status = {
            ST.NO_DATA: [],
            ST.BUSY: [],
            ST.NOT_BUSY: [],
        }
        for item in Drainer(q):
            if item.is_busy is None:
                sort_account_to_status[ST.NO_DATA].append(str(item))
            elif item.is_busy is True:
                sort_account_to_status[ST.BUSY].append(str(item))
                item.is_busy = None
            elif item.is_busy is False:
                sort_account_to_status[ST.NOT_BUSY].append(str(item))
                item.is_busy = None

        return sort_account_to_status
