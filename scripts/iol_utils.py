import json
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from dotenv import load_dotenv
import os
import argparse

BASE_URL = "https://api.invertironline.com/api/v2/"


def load_config():
    file_path = os.getenv("ALGTRAD_PATH", "")
    if not file_path:
        print("Unable to load config fron .env file")
        raise EnvironmentError("ALGTRAD_PATH environment variable is not set. Cannot load .env file.")
    load_dotenv(file_path + ".env")


def get_auth_token(username: str, password: str) -> str:

    data = urlencode(
        {
            "username": username,
            "password": password,
            "grant_type": "password",
        }
    ).encode("utf-8")

    request = Request(
        "https://api.invertironline.com/token",
        data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded",
                 "Accept": "application/json",
                 "User-Agent": "curl/8.7.1",
                 },
        method="POST",
    )

    with urlopen(request) as response:
        payload = json.loads(response.read().decode("utf-8"))

    token = payload.get("access_token")
    if not token:
        raise ValueError(f"Token not found in response: {payload}")

    return token


def request(url: str,
            data: dict,
            token: str,
            method: str = "GET") -> dict:
    """
    Send a method request with content_type data and return the JSON response.

    Args:
        url: Endpoint URL.
        data: Form fields to send in the request body.
        headers: Optional HTTP headers to include in the request.

    Returns:
        Parsed JSON response as a dictionary.
    """

    request_headers = {"Content-Type": "application/json",
                       "Accept": "application/json",
                       "User-Agent": "curl/8.7.1",
                       "Authorization": f"Bearer {token}",
                       }

    request = Request(
            url,
            data=urlencode(data).encode("utf-8"),
            headers=request_headers,
            method=method,
            )
    with urlopen(request) as response:
        body = response.read().decode("utf-8").strip()
        if not body:
            return {}
    return json.loads(body)


def get_instruments_quotes(token: str) -> list[str]:
    """
    url = f"{BASE_URL}/Cotizaciones/{instrument}/{country}/Todos"
    Fetches a list of all available instruments for a given country and instrument type.
    example: Cedears, Stocks, Bonds, etc.
    instrument_types = [
        "opciones",
        "cedears",
        "acciones",
        "aDRs",
        "titulosPublicos",
        "cauciones",
        "cHPD",
        "futuros",
        "obligacionesNegociables",
        "letras",
    ]
    countries = ["argentina", "estados_unidos"]
    """

    url = f"{BASE_URL}/Cotizaciones/cedears/argentina/Todos"
    data = {}
    response = request(url, data, token, method="GET")
    tickers = [t["simbolo"] for t in response.get("titulos", []) if "simbolo" in t]
    print("Tickers -> ", tickers[:4], "...", len(tickers), "total")
    return tickers


command_map = {
    "iquotes": get_instruments_quotes,
}


def exec_command(command: str, username: str, password: str):
    command_func = command_map.get(command, None)
    if command_func:
        token = get_auth_token(username, password)
        command_func(token)
    else:
        print(f"Unknown command: {command}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command")
    # parser.add_argument("--tickers", nargs="+", help="List of tickers to query")
    load_config()
    username = os.getenv("IOL_USERNAME", "")
    password = os.getenv("IOL_PASSWORD", "")
    args = parser.parse_args()

    exec_command(args.command, username, password)

    # print("The token is:", token
