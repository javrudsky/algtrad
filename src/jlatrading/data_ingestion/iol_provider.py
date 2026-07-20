import json
import time
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from concurrent.futures import ThreadPoolExecutor, as_completed


from .model_mapper import IolModelMapper
from .provider import MarketProvider
from ..common.app_logger import AppLogger


# https://api.invertironline.com/token
# POST /token HTTP/1.1
# Host: api.invertironline.com
# Content-Type: application/x-www-form-urlencoded
# username=MIUSUARIO&password=MICONTRASEÑA&grant_type=password


# POST /token HTTP/1.1
# Host: api.invertironline.com
# Content-Type: application/x-www-form-urlencoded
# refresh_token=bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb&grant_type=refresh_token


logger = AppLogger.get_logger(__name__)


class IolClient:
    """
    Client for authenticating and sending POST requests to the InvertirOnline API.

    The client manages OAuth authentication by requesting an access token with
    username and password, refreshing the token when it expires, and attaching
    the token to authenticated POST requests.

    Attributes:
        username: InvertirOnline account username.
        password: InvertirOnline account password.
        access_token: Current access token returned by the API.
        refresh_token: Current refresh token returned by the API.
        expires_at: Expiration time of the access token as a Unix timestamp.
    """

    DEFAULT_COUNTRY = "argentina"
    BASE_URL = "https://api.invertironline.com"
    API_VERSION = "/api/v2"
    TOKEN_URL = f"{BASE_URL}/token"
    API_URL = f"{BASE_URL}{API_VERSION}"

    @classmethod
    def tickers_url(cls, instrument_type: str, country=DEFAULT_COUNTRY) -> str:
        return f"{cls.API_URL}/Cotizaciones/{instrument_type}/{country}/Todos"

    def __init__(self, username: str, password: str) -> None:
        """
        Initialize the client with InvertirOnline user credentials.

        Args:
            username: InvertirOnline account username.
            password: InvertirOnline account password.
        """

        self.username = username
        self.password = password
        self.access_token = None
        self.refresh_token = None
        self.expires_at = 0.0

    def _request(self, url: str,
                 params: dict | None = None,
                 data: dict | None = None,
                 headers: dict | None = None,
                 method: str = "GET",
                 content_type: str = "application/json") -> dict:
        """
        Send a method request with content_type data and return the JSON response.

        Args:
            url: Endpoint URL.
            data: Form fields to send in the request body.
            headers: Optional HTTP headers to include in the request.

        Returns:
            Parsed JSON response as a dictionary.
        """

        request_headers = {"Content-Type": content_type,
                           "Accept": "application/json",
                           "User-Agent": "curl/8.7.1",
                           }

        if headers:
            request_headers.update(headers)

        if params is not None:
            url = f"{url}?{urlencode(params)}"

        encoded_data = None
        if data is not None:
            if content_type == "application/x-www-form-urlencoded":
                encoded_data = urlencode(data).encode("utf-8")
            else:
                encoded_data = json.dumps(data).encode("utf-8")

        logger.d(f"Making {method} request to {url} with headers: {request_headers}")

        request = Request(
            url,
            data=encoded_data,
            headers=request_headers,
            method=method,
        )
        with urlopen(request) as response:
            body = response.read().decode("utf-8").strip()
            if not body:
                return {}
        return json.loads(body)

    def _update_tokens(self, payload: dict) -> str:
        """
        Update stored tokens and expiration time from an authentication response.

        Args:
            payload: JSON response containing token information.

        Returns:
            The updated access token.

        Raises:
            ValueError: If the response does not contain an access token.
        """
        self.access_token = payload.get("access_token")
        self.refresh_token = payload.get("refresh_token", self.refresh_token)

        expires_in = int(payload.get("expires_in", 0))
        self.expires_at = time.time() + max(expires_in - 30, 0)

        if not self.access_token:
            raise ValueError(f"access_token not found in response: {payload}")

        return self.access_token

    def _authenticate(self) -> str:
        """
        Authenticate with username and password and store the returned tokens.

        Returns:
            The new access token.
        """

        logger.d("Authenticating IOL Client")
        payload = self._request(
            self.TOKEN_URL,
            data={
                "username": self.username,
                "password": self.password,
                "grant_type": "password",
                },
            method="POST",
            content_type="application/x-www-form-urlencoded"
        )
        return self._update_tokens(payload)

    def _refresh_access_token(self) -> str:
        """
        Renew the access token using the stored refresh token.

        Returns:
            The new access token.

        Raises:
            ValueError: If no refresh token is available.
        """

        if not self.refresh_token:
            raise ValueError("refresh_token is not set")

        payload = self._request(
            self.TOKEN_URL,
            data={
                "refresh_token": self.refresh_token,
                "grant_type": "refresh_token",
                },
            method="POST",
            content_type="application/x-www-form-urlencoded"
        )
        return self._update_tokens(payload)

    def _ensure_token(self) -> str:
        """
        Return a valid access token, refreshing or requesting one if needed.

        Returns:
            A valid access token.
        """

        if not self.access_token:
            return self._authenticate()

        if time.time() >= self.expires_at:
            return self._refresh_access_token()

        return self.access_token

    def _get(self, url: str, params: dict | None = None, data: dict | None = None) -> dict:
        """
        Send a GET request and optionally include authentication headers.

        If authentication is enabled, this method ensures the access token is valid
        before making the request.

        Args:
            url: Endpoint URL.
            data: Form fields to send in the request body.
            use_auth: Whether to include the Bearer token in the request.

        Returns:
            Parsed JSON response as a dictionary.
        """

        headers = {}
        token = self._ensure_token()
        headers["Authorization"] = f"Bearer {token}"

        return self._request(url, params=params, data=data, headers=headers, method="GET")

    def get_prices_by_instrument_type(self, instrument_type: str = "acciones") -> dict:
        """
        Retrieve a list of available tickers for the specified instrument type.

        Args:
            instrument_type: Type of financial instrument (e.g., "Acciones", "Bonos").

        Returns:
            A list of dictionaries containing ticker information.
        """

        url = self.tickers_url(instrument_type)
        logger.d(f"Fetching prices for instrument type: {instrument_type} from URL: {url}")
        response = self._get(url)
        return response


class IolProvider(MarketProvider):
    INSTRUMENT_TYPES = [
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

    def __init__(self, iol_client: IolClient):
        self.iol_client = iol_client

    def download_instruments_prices(self) -> list[dict]:
        """Return a list of available market tickers."""

        ins = self.INSTRUMENT_TYPES
        fnc = self.iol_client.get_prices_by_instrument_type
        data = []
        with ThreadPoolExecutor(max_workers=3) as executor:
            future_to_value = {executor.submit(fnc, i): i for i in ins}
            for future in as_completed(future_to_value):
                logger.d(f"Attempting to download data for value: {future_to_value[future]}")
                instrument_type = future_to_value[future]
                try:
                    instruments = future.result().get("titulos", [])
                    instruments = IolModelMapper.map_instruments_prices(instruments, option_type=instrument_type)
                    logger.d(f"Downloaded data for value {instrument_type}: {instruments}")
                    data.extend(instruments)
                except Exception as exc:
                    logger.e(f"Value {instrument_type} failed: {exc}")
        return data

    def download_daily_bar(self,
                           tickers: list[str],
                           start_date: str,
                           end_date: str) -> str:

        logger.w(f"Calling unimplemented method IOL download_daily_bar with params {tickers}: {start_date} to {end_date}")
        # Using yfinance provider for now
        return "[]"
