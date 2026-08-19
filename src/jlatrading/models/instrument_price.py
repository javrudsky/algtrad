from pydantic import BaseModel, ConfigDict, Field, AliasPath


class InstrumentPrice(BaseModel):
    model_config = ConfigDict(extra="ignore")

    symbol: str = Field(validation_alias="simbolo")
    bid_quantity: int = Field(default=0, validation_alias=AliasPath("puntas", "cantidadCompra"))
    bid_price: float = Field(default=0.0, validation_alias=AliasPath("puntas", "precioCompra"))
    ask_price: float = Field(default=0.0, validation_alias=AliasPath("puntas", "precioVenta"))
    ask_quantity: int = Field(default=0, validation_alias=AliasPath("puntas", "cantidadVenta"))
    last_price: float = Field(default=0.0, validation_alias="ultimoPrecio")
    percent_change: float = Field(default=0.0, validation_alias="variacionPorcentual")
    open_price: float = Field(default=0.0, validation_alias="apertura")
    high_price: float = Field(default=0.0, validation_alias="maximo")
    low_price: float = Field(default=0.0, validation_alias="minimo")
    previous_close: float = Field(default=0.0, validation_alias="ultimoCierre")
    volume: int = Field(default=0, validation_alias="volumen")
    operations_count: int = Field(default=0, validation_alias="cantidadOperaciones")
    timestamp: str | None = Field(validation_alias="fecha")
    option_type: str | None = Field(validation_alias="tipoOpcion")
    strike_price: float = Field(validation_alias="precioEjercicio")
    expiration_date: str = Field(validation_alias="fechaVencimiento")
    market: str = Field(validation_alias="mercado")
    currency: str = Field(validation_alias="moneda")
    description: str = Field(default="", validation_alias="descripcion")
    settlement_term: str = Field(validation_alias="plazo")
    minimum_lot_size: int = Field(validation_alias="laminaMinima")
    lot_size: int = Field(default=0, validation_alias="lote")
