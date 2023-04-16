import logging, time
from logging.handlers import RotatingFileHandler

from core.presenter import Presenter
from core.processing import MultiCheckHandler
from core.status import Status

from core.drivers import DriversHandler


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
    Интерфейс, объединяющий в одну функцию.
    """

    def __init__(self, regional: bool) -> None:
        self.regional = regional

    def perform_not_busy(self, drivers):

        handler = MultiCheckHandler(regional=self.regional)
        q = handler.processing(drivers=drivers)
        presentation = Presenter().composing(q)

        logger.info(presentation)

        return ', '.join(presentation[Status.NOT_BUSY])

drivers_handler = DriversHandler()
drivers_handler.create_drivers()
drivers = drivers_handler.drivers
start = time.time()
print(Commander(regional=False).perform_not_busy(drivers=drivers))
print(time.time() - start)
for driver in drivers:
    driver.quit()