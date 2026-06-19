from typing import Protocol

# Common
from ..common.config import AppConfig
from ..common.app_logger import AppLogger
from ..common.exceptions import DbError


# Providers
from ..data_ingestion.provider import MarketProvider
from ..data_ingestion.yfinance_provider import YFinanceProvider, BaseYFinanceWrapper, YFinanceWrapper

# Services
from ..data_ingestion.service import MarketService

# Repositories
from ..repository.repository import Repository
from ..repository.daily_bar_repo import DailyBarRepo

# Database
from ..database.db import Db
from ..database.duck_db import DuckDb

logger = AppLogger.get_logger(__name__)


class ComponentFactory(Protocol):

    @staticmethod
    def daily_bar_repo(db: Db) -> DailyBarRepo:
        return DailyBarRepo(db)

    @staticmethod
    def market_provider(yf_client: BaseYFinanceWrapper | None = None) -> MarketProvider:
        if yf_client is None:
            yf_client = YFinanceWrapper()
        return YFinanceProvider(yf_client)

    @staticmethod
    def market_service(market_provider: MarketProvider,
                       daily_bar_repo: Repository) -> MarketService:
        return MarketService(market_provider, daily_bar_repo)

    @staticmethod
    def db(path: str) -> Db:
        return DuckDb(path)

    @staticmethod
    def build_market_service(db_path: str | None = None) -> MarketService:

        if db_path is None:
            root_path = AppConfig.get_value('ALGTRAD_PATH', "")
            db_path = AppConfig.get_value('DATABASE_PATH', "")
            if db_path is None or db_path.strip() == "" or \
                    root_path is None or root_path.strip() == "":
                logger.e(f"Missing database path configuration. ALGTRAD_PATH: {root_path}, DATABASE_PATH: {db_path}")
                raise DbError("Database path must be provided either as an argument or in the configuration")

            db_path = f"{root_path}{db_path}"

        logger.d(f"Opening database at path: {db_path}")
        db = ComponentFactory.db(db_path)
        db.connect()
        daily_bar_repo = ComponentFactory.daily_bar_repo(db)
        market_provider = ComponentFactory.market_provider()
        market_service = ComponentFactory.market_service(market_provider, daily_bar_repo)
        return market_service
