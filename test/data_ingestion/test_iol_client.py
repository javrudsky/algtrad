import json
from unittest.mock import MagicMock, patch

import pytest

from jlatrading.data_ingestion.iol_provider import IolClient


def make_urlopen_response(body: str):
    response = MagicMock()
    response.read.return_value = body.encode("utf-8")

    context_manager = MagicMock()
    context_manager.__enter__.return_value = response
    context_manager.__exit__.return_value = None
    return context_manager


def test_tickers_url_uses_default_country():
    assert (
        IolClient.tickers_url("acciones")
        == "https://api.invertironline.com/api/v2/Cotizaciones/acciones/argentina/Todos"
    )


def test_tickers_url_allows_custom_country():
    assert (
        IolClient.tickers_url("bonos", country="usa")
        == "https://api.invertironline.com/api/v2/Cotizaciones/bonos/usa/Todos"
    )


def test_init_sets_default_state():
    client = IolClient("user", "pass")

    assert client.username == "user"
    assert client.password == "pass"
    assert client.access_token is None
    assert client.refresh_token is None
    assert client.expires_at == 0.0


@patch("jlatrading.data_ingestion.iol_provider.urlopen")
def test_request_posts_form_data_and_returns_json(mock_urlopen):
    payload = {"ok": True}
    mock_urlopen.return_value = make_urlopen_response(json.dumps(payload))
    client = IolClient("user", "pass")

    result = client._request(
        "https://example.com/test",
        data={"username": "user", "grant_type": "password"},
        headers={"Authorization": "Bearer abc"},
        content_type="application/x-www-form-urlencoded",
    )

    assert result == payload

    request = mock_urlopen.call_args.args[0]
    assert request.full_url == "https://example.com/test"
    assert request.get_method() == "GET"
    assert request.data.decode("utf-8") == "username=user&grant_type=password"
    assert request.headers["Content-type"] == "application/x-www-form-urlencoded"
    assert request.headers["Accept"] == "application/json"
    assert request.headers["User-agent"] == "curl/8.7.1"
    assert request.headers["Authorization"] == "Bearer abc"


@patch("jlatrading.data_ingestion.iol_provider.urlopen")
def test_request_returns_empty_dict_for_empty_body(mock_urlopen):
    mock_urlopen.return_value = make_urlopen_response("")
    client = IolClient("user", "pass")

    result = client._request("https://example.com/test", data={})

    assert result == {}


def test_update_tokens_sets_state_and_returns_access_token():
    client = IolClient("user", "pass")

    with patch("jlatrading.data_ingestion.iol_provider.time.time", return_value=1000):
        token = client._update_tokens(
            {
                "access_token": "access-123",
                "refresh_token": "refresh-123",
                "expires_in": 120,
            }
        )

    assert token == "access-123"
    assert client.access_token == "access-123"
    assert client.refresh_token == "refresh-123"
    assert client.expires_at == 1090


def test_update_tokens_keeps_existing_refresh_token_when_missing():
    client = IolClient("user", "pass")
    client.refresh_token = "existing-refresh"

    with patch("jlatrading.data_ingestion.iol_provider.time.time", return_value=1000):
        client._update_tokens(
            {
                "access_token": "access-123",
                "expires_in": 60,
            }
        )

    assert client.refresh_token == "existing-refresh"


def test_update_tokens_raises_when_access_token_missing():
    client = IolClient("user", "pass")

    with pytest.raises(ValueError, match="access_token not found"):
        client._update_tokens({"expires_in": 120})


@patch("jlatrading.data_ingestion.iol_provider.time.time", return_value=1000)
@patch("jlatrading.data_ingestion.iol_provider.urlopen")
def test_authenticate_requests_password_grant(mock_urlopen, _mock_time):
    payload = {
        "access_token": "new-access",
        "refresh_token": "new-refresh",
        "expires_in": 120,
    }
    mock_urlopen.return_value = make_urlopen_response(json.dumps(payload))
    client = IolClient("javi", "pass_javi")

    token = client._authenticate()

    assert token == "new-access"
    assert client.access_token == "new-access"
    assert client.refresh_token == "new-refresh"
    assert client.expires_at == 1090

    request = mock_urlopen.call_args.args[0]
    assert request.full_url == IolClient.TOKEN_URL
    assert request.data.decode("utf-8") == (
        "username=javi&password=pass_javi&grant_type=password"
    )
    assert request.headers["Content-type"] == "application/x-www-form-urlencoded"


def test_refresh_access_token_raises_without_refresh_token():
    client = IolClient("user", "pass")

    with pytest.raises(ValueError, match="refresh_token is not set"):
        client._refresh_access_token()


@patch("jlatrading.data_ingestion.iol_provider.time.time", return_value=2000)
@patch("jlatrading.data_ingestion.iol_provider.urlopen")
def test_refresh_access_token_requests_refresh_grant(mock_urlopen, _mock_time):
    payload = {
        "access_token": "refreshed-access",
        "refresh_token": "refreshed-refresh",
        "expires_in": 90,
    }
    mock_urlopen.return_value = make_urlopen_response(json.dumps(payload))
    client = IolClient("user", "pass")
    client.refresh_token = "old-refresh"

    token = client._refresh_access_token()

    assert token == "refreshed-access"
    assert client.access_token == "refreshed-access"
    assert client.refresh_token == "refreshed-refresh"
    assert client.expires_at == 2060

    request = mock_urlopen.call_args.args[0]
    assert request.full_url == IolClient.TOKEN_URL
    assert request.data.decode("utf-8") == (
        "refresh_token=old-refresh&grant_type=refresh_token"
    )
    assert request.headers["Content-type"] == "application/x-www-form-urlencoded"


def test_ensure_token_authenticates_when_access_token_missing():
    client = IolClient("user", "pass")

    with patch.object(
        client, "_authenticate", return_value="fresh-token"
    ) as mock_auth:
        token = client._ensure_token()

    assert token == "fresh-token"
    mock_auth.assert_called_once_with()


def test_ensure_token_refreshes_when_expired():
    client = IolClient("user", "pass")
    client.access_token = "expired-token"
    client.expires_at = 1000

    with patch("jlatrading.data_ingestion.iol_provider.time.time", return_value=1001):
        with patch.object(
            client, "_refresh_access_token", return_value="renewed-token"
        ) as mock_refresh:
            token = client._ensure_token()

    assert token == "renewed-token"
    mock_refresh.assert_called_once_with()


def test_ensure_token_returns_existing_token_when_valid():
    client = IolClient("user", "pass")
    client.access_token = "valid-token"
    client.expires_at = 2000

    with patch("jlatrading.data_ingestion.iol_provider.time.time", return_value=1000):
        with patch.object(
            client, "_refresh_access_token"
        ) as mock_refresh:
            token = client._ensure_token()

    assert token == "valid-token"
    mock_refresh.assert_not_called()


def test_get_calls_request_with_bearer_token():
    client = IolClient("user", "pass")

    with patch.object(
        client, "_ensure_token", return_value="test-token"
    ) as mock_ensure:
        with patch.object(
            client, "_request", return_value={"ok": True}
        ) as mock_request:
            result = client._get("https://example.com/quotes")

    assert result == {"ok": True}
    mock_ensure.assert_called_once_with()
    mock_request.assert_called_once_with(
        "https://example.com/quotes",
        params=None,
        data=None,
        headers={"Authorization": "Bearer test-token"},
        method="GET",
    )


def test_get_prices_by_instrument_type_uses_private_get():
    client = IolClient("user", "pass")
    payload = {
        "titulos": [
            {
                "simbolo": "AAL",
                "ultimoPrecio": 12500,
                "descripcion": "Cedear American Airlines Group",
            },
            {
                "simbolo": "AALC",
                "ultimoPrecio": 8.16,
                "descripcion": "Cedear American Airlines Group",
            },
        ]
    }

    with patch.object(client, "_get", return_value=payload) as mock_get:
        result = client.get_prices_by_instrument_type("acciones")

    assert result == payload
    mock_get.assert_called_once_with(
        "https://api.invertironline.com/api/v2/Cotizaciones/acciones/argentina/Todos",
    )
