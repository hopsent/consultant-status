from datetime import datetime, timezone


class PreviuosMessageContainer:
    """
    Хранит сведения о предыдущей команде,
    полученной программой от человека.
    """

    def __init__(self, date: datetime = datetime.now(tz=timezone.utc)) -> None:
        self.date = date
