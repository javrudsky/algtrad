from .repository import Repository
from .view import DbView


class Storage:

    def __init__(self,
                 daily_bar_repo: Repository,
                 instruments_price_repo: Repository,
                 daily_bar_summary_view: DbView):

        self.daily_bar_repo = daily_bar_repo
        self.instrument_price_repo = instruments_price_repo
        self.daily_bar_summary_view = daily_bar_summary_view
