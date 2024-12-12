from typing import List
from multiprocessing import Process, Queue

from core.emulating import Emulator


class MultiCheckHandler:
    """
    Запускаем мультипоточность в этом классе.
    """

    def __init__(self) -> None:
        pass

    def check_account(self, window: Emulator, q: Queue) -> None:
        """
        В очереди эмулируем поведение человека в открытых
        окнах браузера.
        """

        status = window.check_account_is_busy()
        q.put_nowait(status)

    def processing(self, windows: List[Emulator]) -> Queue:
        """
        Разбивает исполнение программы на процессы, чтобы,
        одновременно исследовался статус
        нескольких аккаунтов на сайте.
        Возвращает очередь q из объектов Account.
        """

        processes = []
        q = Queue()

        for i in range(len(windows)):
            p = Process(
                target=self.check_account,
                args=(windows[i], q)
            )
            processes.append(p)
            p.start()

        [p.join() for p in processes]

        return q
