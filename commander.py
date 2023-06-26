import logging
from logging.handlers import RotatingFileHandler

from core.presenter import Presenter
from core.processing import MultiCheckHandler
from core.status import Status


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


class Commander:
    """
    Интерфейс, объединяющий несколько программ для
    использования в качестве команды в интерфейсе
    телеграм-бота, в частности объединяются:
    (1) хендлер, отвечающий за мультипоточность; -
    на объекте хендлера вызывается метод processing(),
    запускающий потоковую проверку статуса аккаунтов;
    (2) презентер информации, полученной из очереди,
    являющейся результатом работы метода processing().

    Результат объединения - словарь с ключами, отвечающими
    бизнес-логике: 'not_busy' - свободные аккаунты и
    'no_data' - техническая информация на случай проблем с
    работой программ.
    """

    def __init__(self, regional: bool) -> None:
        self.regional = regional

    def perform_not_busy(self, drivers):

        handler = MultiCheckHandler(regional=self.regional)
        q = handler.processing(drivers=drivers)
        presentation = Presenter().composing(q)

        logger.info(presentation)

        return {
            Status.NOT_BUSY: ', '.join(presentation[Status.NOT_BUSY]),
            Status.NO_DATA: ', '.join(presentation[Status.NO_DATA]),
        }
