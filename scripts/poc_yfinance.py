import os
import pandas as pd
import yfinance as yf
from dotenv import load_dotenv

# #######################
# yfinance dowload sample

# Price            Close                    High                     Low                    Open                Volume
# Ticker            AAPL        MSFT        AAPL        MSFT        AAPL        MSFT        AAPL        MSFT      AAPL      MSFT
# Date
# 2024-01-02  183.562180  363.801483  186.330843  368.735614  181.831767  359.779620  185.055273  366.734486  82488700  25258600
# 2024-01-03  182.187744  363.536621  183.799505  366.145927  181.376915  361.486459  182.158081  361.976929  58414500  23083500
# 2024-01-04  179.873932  360.927368  181.040717  365.989026  178.855462  360.172055  180.111236  363.605347  71983600  20901500
# #######################

# data = (
#         data.stack(level="Ticker")
#         .reset_index()
#         .rename(columns={"level_1": "Ticker"})
#         )

# df = yf.download(["AAPL", "MSFT"], start="2024-01-01", end="2024-01-31", interval="1d")

# df = pd.DataFrame({"my_pivot": [10, 20, 10, 20, 10, 20],
#                    "my_index": [40, 40, 60, 60, 80, 80],
#                    "c3": [77, 88, 90, 99, 10, 11],
#                    "c4": [10, 11, 12, 15, 22, 23]})


# print(df)
# df = df.pivot(index="my_index", columns="my_pivot", values=["c3", "c4"])
# print(df)

# df = df.stack(level="my_pivot")
# print(df)

# df = df.reset_index()
# print(df)
def load_config():
    file_path = os.getenv("ALGTRAD_PATH", "")
    if not file_path:
        print("Unable to load config fron .env file")
        raise EnvironmentError("ALGTRAD_PATH environment variable is not set. Cannot load .env file.")
    load_dotenv(file_path + ".env")


def mock_yfinance_data():
    dfy = pd.DataFrame({"Ticker": ["YPF", "YPF", "AAL", "AAL", "GGAL", "GGAL"],
                        "Date": ["2024-01-01", "2024-01-02", "2024-01-01", "2024-01-02", "2024-01-01", "2024-01-02"],
                        "Open": [10, 20, 30, 40, 50, 60],
                        "High": [12, 22, 32, 42, 52, 62],
                        "Low": [8, 18, 28, 38, 48, 58],
                        "Close": [15, 25, 35, 45, 55, 65],
                        "Volume": [100, 200, 300, 400, 500, 600]})

    print(dfy)
    dfy = dfy.pivot(index="Date", columns="Ticker", values=["Open", "High", "Low", "Close", "Volume"])
    print("______________")
    print(dfy)
    dfy.columns.names = ["Price", "Ticker_"]
    print("______________")
    print(dfy)


data_path = ""


# TODO: Implement a service / provider / repo / db layer and tests
# Saving a comma separated file for now
def get_tickers_info(tickers: list[str]):
    """Get the information of a ticker using yfinance."""
    global data_path
    sectors = []
    industries = []
    for ticker in tickers[:2]:
        t = yf.Ticker(f"{ticker.strip()}.BA")
        print("info:", t.info)
        sector = t.info.get("sectorKey", "no-sector")
        industry = t.info.get("industryKey", "no-industry")
        sectors.append(sector)
        print("Downloaded -> Ticker: " + ticker + " - Sector: " + sector + " - Industry: " + industry)
        industries.append(industry)

    df = pd.DataFrame({"ticker": tickers, "sector": sectors, "industry": industries})
    df.to_csv(f"{data_path}sectors.csv", index=False)


def main():
    load_config()
    tickers = os.getenv("DEFAULT_TICKERS", "")
    root_path = os.getenv("ALGTRAD_PATH", "")
    global data_path
    data_path = os.getenv("DATA_PATH", "")
    data_path = root_path + data_path
    if tickers == "":
        print("DEFAULT_TICKERS environment variable is not set. Please set it in the .env file.")
        return
    if data_path == "":
        print("DATA_PATH environment variable is not set. Please set it in the .env file.")
        return

    print("Retrieving sectors for tickers: " + tickers)
    tickers = tickers.split(",")
    get_tickers_info(tickers)


if __name__ == "__main__":
    main()
