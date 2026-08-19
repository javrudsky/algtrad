from .repository import Repository


class Storage:

    def __init__(self,
                 daily_bar_repo: Repository,
                 instruments_price_repo: Repository):
        self.daily_bar_repo = daily_bar_repo
        self.instrument_price_repo = instruments_price_repo
