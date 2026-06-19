from unittest.mock import Mock

from jlatrading.common.config import AppConfig, TypedValue


def test_typed_value_to_int_returns_integer() -> None:
    raw_value = "123"
    expected_value = 123

    typed_value = TypedValue(raw_value)

    result = typed_value.to_int()

    assert result == expected_value


def test_typed_value_to_int_returns_default_for_invalid_value() -> None:
    raw_value = "abc"
    default_value = 99

    typed_value = TypedValue(raw_value)

    result = typed_value.to_int(default=default_value)

    assert result == default_value


def test_typed_value_to_int_returns_default_for_none() -> None:
    raw_value = None
    default_value = 7

    typed_value = TypedValue(raw_value)

    result = typed_value.to_int(default=default_value)

    assert result == default_value


def test_typed_value_to_strlist_splits_and_strips_values() -> None:
    raw_value = "AAPL, MSFT , GOOGL"
    expected_value = ["AAPL", "MSFT", "GOOGL"]

    typed_value = TypedValue(raw_value)

    result = typed_value.to_strlist()

    assert result == expected_value


def test_typed_value_to_strlist_returns_default_for_none() -> None:
    raw_value = None
    default_value = ["MELI.BA", "YPFD.BA"]

    typed_value = TypedValue(raw_value)

    result = typed_value.to_strlist(default=default_value)

    assert result == default_value


def test_typed_value_to_strlist_returns_empty_list_for_none_without_default() -> None:
    raw_value = None
    expected_value: list[str] = []

    typed_value = TypedValue(raw_value)

    result = typed_value.to_strlist()

    assert result == expected_value


def test_typed_value_to_strlist_returns_default_for_invalid_type() -> None:
    raw_value = 123
    default_value = ["AAPL"]

    typed_value = TypedValue(raw_value)

    result = typed_value.to_strlist(default=default_value)

    assert result == default_value


def test_app_config_load_config_calls_load_dotenv(monkeypatch) -> None:

    algpath_path = "/app/"

    # Mocking os.getenv to return the desired path for ALGTRAD_PATH variable.
    def fake_getenv(key, default=None):
        if key == "ALGTRAD_PATH":
            return algpath_path
        return "wrong path"

    os_getenv = Mock()
    os_getenv.getenv = fake_getenv
    monkeypatch.setattr("jlatrading.common.config.os.getenv", os_getenv.getenv)

    expected_path = f"{algpath_path}/.env"
    load_dotenv_mock = Mock()

    monkeypatch.setattr("jlatrading.common.config.load_dotenv", load_dotenv_mock)

    AppConfig.load_config()

    load_dotenv_mock.assert_called_once_with(expected_path)


def test_app_config_get_value_returns_environment_value(monkeypatch) -> None:
    key = "TEST_CONFIG_KEY"
    expected_value = "configured-value"

    monkeypatch.setenv(key, expected_value)

    result = AppConfig.get_value(key)

    assert result == expected_value


def test_app_config_get_value_returns_default_when_missing(monkeypatch) -> None:
    key = "MISSING_TEST_CONFIG_KEY"
    default_value = "default-value"

    monkeypatch.delenv(key, raising=False)

    result = AppConfig.get_value(key, default=default_value)

    assert result == default_value


def test_app_config_get_typed_value_returns_typed_value(monkeypatch) -> None:
    key = "DEFAULT_TICKERS"
    raw_value = "AAPL,MSFT"
    expected_value = ["AAPL", "MSFT"]

    monkeypatch.setenv(key, raw_value)

    result = AppConfig.get_typed_value(key)

    assert isinstance(result, TypedValue)
    assert result.to_strlist() == expected_value
