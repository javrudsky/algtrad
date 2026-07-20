from jlatrading.database.db_helper import DbHelper


def test_normalize_sql_replaces_newlines_collapses_spaces_and_trims():
    value = "  SELECT   *\nFROM   instrument_price\n WHERE   symbol = 'AAL'  "

    result = DbHelper.normalize_sql(value)

    assert result == "SELECT * FROM instrument_price WHERE symbol = 'AAL'"


def test_normalize_sql_returns_empty_string_for_whitespace_only_input():
    value = " \n   \t  \n "

    result = DbHelper.normalize_sql(value)

    assert result == ""


def test_quote_identifier_wraps_identifier_in_double_quotes():
    result = DbHelper.quote_identifier("symbol")

    assert result == '"symbol"'


def test_quote_identifier_escapes_embedded_double_quotes():
    result = DbHelper.quote_identifier('my"column')

    assert result == '"my""column"'
