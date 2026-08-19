from ..common.app_logger import AppLogger

logger = AppLogger.get_logger(__name__)


class IolModelMapper:
    # Using simple mapping for now.
    @staticmethod
    def map_instrument_price(data: dict, option_type: str) -> dict:
        """Map a single InvertirOnline instrument price payload to the flat database schema.

        Args:
            data: Dictionary containing the raw instrument price payload.

        Returns:
            A dictionary with normalized English keys matching the instrument_price table.
        """
        order_book = data.get("puntas", {})
        if order_book is None:
            order_book = {}

        return {
            "symbol": data.get("simbolo"),
            "bid_quantity": order_book.get("cantidadCompra", 0),
            "bid_price": order_book.get("precioCompra", 0.0),
            "ask_price": order_book.get("precioVenta", 0.0),
            "ask_quantity": order_book.get("cantidadVenta", 0),
            "close_price": data.get("ultimoPrecio", 0.0),
            "percent_change": data.get("variacionPorcentual", 0.0),
            "open_price": data.get("apertura", 0.0),
            "high_price": data.get("maximo", 0.0),
            "low_price": data.get("minimo", 0.0),
            "previous_close": data.get("ultimoCierre", 0.0),
            "volume": data.get("volumen", 0),
            "operations_count": data.get("cantidadOperaciones", 0),
            "timestamp": data.get("fecha"),
            # "option_type": data.get("tipoOpcion", MISSING),
            # Option TYpe comes null from the IOL API, but passed as parameter when hitting the endpoint
            "option_type": option_type,
            "strike_price": data.get("precioEjercicio", 0.0),
            "expiration_date": data.get("fechaVencimiento"),
            "market": data.get("mercado"),
            "currency": data.get("moneda"),
            "description": data.get("descripcion", ""),
            "settlement_term": data.get("plazo"),
            "minimum_lot_size": data.get("laminaMinima", 0),
            "lot_size": data.get("lote", 0),
        }

    @staticmethod
    def map_instruments_prices(items: list[dict], option_type: str) -> list[dict]:
        """Map multiple InvertirOnline instrument price payloads to the flat database schema.

        Args:
            items: List of dictionaries containing raw instrument price payloads.

        Returns:
            A list of dictionaries with normalized English keys matching the
            instrument_price table.
        """
        return [IolModelMapper.map_instrument_price(item, option_type=option_type) for item in items]


class YfinanceModelMapper:
    @staticmethod
    def map_daily_bar(data: dict) -> list[dict]:
        """Map a single yfinance daily bar payload to the flat database schema.

        Args:
            data: Dictionary containing the raw daily bar payload.

        Returns:
            A list of dictionaries with normalized English keys matching the daily_bar table.
        """
        mapped_data = []
        for ticker, df in data.items():
            for index, row in df.iterrows():
                mapped_data.append({
                    "ticker": ticker,
                    "date": int(index.timestamp()),
                    "open": row["Open"],
                    "high": row["High"],
                    "low": row["Low"],
                    "close": row["Close"],
                    "volume": int(row["Volume"]),
                })
        return mapped_data
