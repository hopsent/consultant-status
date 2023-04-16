from queue import Empty
from multiprocessing import Queue
from typing import Generator


class Drainer(object):
    """
    Интерфейс, предназначенный для распаковки очереди,
    образованной по результатам разделения программы на процессы.
    В очереди находятся аккаунты.
    """

    def __init__(self, q: Queue):
        self.q = q

    def __iter__(self) -> Generator:
        """
        Итерируем очередь q до тех пор, пока
        очередь не будет пустой. Образуется генератор
        объектов из очереди.
        """

        while True:
            try:
                yield self.q.get_nowait()
            except Empty:
                break
