from jlatrading.data_ingestion.model_mapper import IolModelMapper

base_data = {
        "simbolo": "AAL",
        "puntas": {
            "cantidadCompra": 19,
            "precioCompra": 12480,
            "precioVenta": 12520,
            "cantidadVenta": 5277,
        },
        "ultimoPrecio": 12500,
        "variacionPorcentual": -2.19,
        "apertura": 12640,
        "maximo": 12660,
        "minimo": 12340,
        "ultimoCierre": 12500,
        "volumen": 6860,
        "cantidadOperaciones": 95,
        "fecha": "2026-07-14T11:36:56.31",
        "tipoOpcion": None,
        "precioEjercicio": None,
        "fechaVencimiento": None,
        "mercado": "1",
        "moneda": "1",
        "descripcion": "Cedear American Airlines Group",
        "plazo": "T1",
        "laminaMinima": 1,
        "lote": 1,
    }

base_result = {
        "symbol": "AAL",
        "bid_quantity": 19,
        "bid_price": 12480,
        "ask_price": 12520,
        "ask_quantity": 5277,
        "close_price": 12500,
        "percent_change": -2.19,
        "open_price": 12640,
        "high_price": 12660,
        "low_price": 12340,
        "previous_close": 12500,
        "volume": 6860,
        "operations_count": 95,
        "timestamp": "2026-07-14T11:36:56.31",
        "option_type": "cedear",
        "strike_price": None,
        "expiration_date": None,
        "market": "1",
        "currency": "1",
        "description": "Cedear American Airlines Group",
        "settlement_term": "T1",
        "minimum_lot_size": 1,
        "lot_size": 1,
    }


def test_map_instrument_price_maps_all_fields_to_flat_schema():
    data = base_data.copy()
    result = IolModelMapper.map_instrument_price(data, option_type="cedear")

    assert result == base_result.copy()


def test_map_instrument_price_maps_all_fields_missing_order_book():
    data = base_data.copy()
    data.pop("puntas", None)

    expected_result = base_result.copy()
    r_fields = ["bid_quantity", "bid_price", "ask_price", "ask_quantity"]
    for key in r_fields:
        expected_result[key] = 0.0

    result = IolModelMapper.map_instrument_price(data, option_type="cedear")

    assert result == expected_result
