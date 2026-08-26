from typing import Protocol

# Common
from ..common.config import AppConfig
from ..common.app_logger import AppLogger
from ..common.exceptions import DbError


# Providers
from ..data_ingestion.provider import MarketProvider
from ..data_ingestion.yfinance_provider import YFinanceProvider, YFinanceWrapper
from ..data_ingestion.iol_provider import IolProvider, IolClient
from ..data_ingestion.compound_provider import CompoundProvider

# Services
from ..data_ingestion.service import BaseMarketService, MarketService
from ..query.service import BaseSystemStatsService, SystemStatsService

# Repositories
from ..repository.storage import Storage
from ..repository.repository import Repository
from ..repository.view import DbView
from ..repository.daily_bar_repo import DailyBarRepo
from ..repository.instrument_price_repo import InstrumentPriceRepo
from ..repository.daily_bar_view import DailyBarSummaryView

# Database
from ..database.db import Db
from ..database.duck_db import DuckDb

logger = AppLogger.get_logger(__name__)


class ComponentFactory(Protocol):

    @staticmethod
    def daily_bar_repo(db: Db) -> Repository:
        return DailyBarRepo(db)

    @staticmethod
    def instruments_prices_repo(db: Db) -> Repository:
        return InstrumentPriceRepo(db)

    @staticmethod
    def daily_bar_summary_view(db: Db) -> DbView:
        return DailyBarSummaryView(db)

    @staticmethod
    def storage(db: Db) -> Storage:
        return Storage(daily_bar_repo=ComponentFactory.daily_bar_repo(db),
                       instruments_price_repo=ComponentFactory.instruments_prices_repo(db),
                       daily_bar_summary_view=ComponentFactory.daily_bar_summary_view(db))

    @staticmethod
    def market_provider() -> MarketProvider:
        yfinance_provider = YFinanceProvider(YFinanceWrapper())

        iol_client = IolClient(username=AppConfig.get_typed_value("IOL_USERNAME", "").to_str(),
                               password=AppConfig.get_typed_value("IOL_PASSWORD", "").to_str())

        iol_provider = IolProvider(iol_client=iol_client)
        return CompoundProvider(iol_provider=iol_provider, yfinance_provider=yfinance_provider)

    @staticmethod
    def market_service(market_provider: MarketProvider,
                       storage: Storage) -> BaseMarketService:
        return MarketService(market_provider, storage)

    @staticmethod
    def system_stats_service(storage: Storage) -> BaseSystemStatsService:
        return SystemStatsService(storage)

    @staticmethod
    def db(path: str) -> Db:
        return DuckDb(path)

    @staticmethod
    def build_db(db_path: str | None = None) -> Db:
        if db_path is None:
            root_path = AppConfig.get_value('ALGTRAD_PATH', "")
            db_path = AppConfig.get_value('DATABASE_PATH', "")
            if db_path is None or db_path.strip() == "" or \
                    root_path is None or root_path.strip() == "":
                logger.e(f"Missing database path configuration. ALGTRAD_PATH: {root_path}, DATABASE_PATH: {db_path}")
                raise DbError("Database path must be provided either as an argument or in the configuration")

            db_path = f"{root_path}{db_path}"

        logger.d(f"Opening database at path: {db_path}")
        return ComponentFactory.db(db_path)

    @staticmethod
    def build_market_service(db_path: str | None = None) -> BaseMarketService:
        db = ComponentFactory.build_db(db_path)
        db.connect()
        storage = ComponentFactory.storage(db)
        market_provider = ComponentFactory.market_provider()
        market_service = ComponentFactory.market_service(market_provider, storage)
        return market_service

    @staticmethod
    def build_system_stats_service(db_path: str | None = None) -> BaseSystemStatsService:
        db = ComponentFactory.build_db(db_path)
        db.connect()
        storage = ComponentFactory.storage(db)
        ss_service = ComponentFactory.system_stats_service(storage)
        return ss_service
