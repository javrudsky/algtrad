# Ticker      YPFD.BA                                     MELI.BA
# Ticker Price          Open     High      Low    Close  Volume     Open     High      Low    Close  Volume Date

from pydantic import BaseModel, Field
from datetime import datetime


class DailyBar(BaseModel):
    ticker: str = Field(description="The ticker symbol of the instrument.")
    date: datetime
    open_price: float = Field(ge=0, alias="open")
    high_price: float = Field(ge=0, alias="high")
    low_price: float = Field(ge=0, alias="low")
    close_price: float = Field(ge=0, alias="close")
    volume: int = Field(ge=0)
