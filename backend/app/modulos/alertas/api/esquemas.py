from datetime import date

from pydantic import BaseModel


class AlertaStockBajo(BaseModel):
    producto_id: int
    nombre: str
    stock: int
    stock_minimo: int


class LotePorVencer(BaseModel):
    producto_id: int
    producto: str
    numero_lote: str
    cantidad: int
    fecha_vencimiento: date
