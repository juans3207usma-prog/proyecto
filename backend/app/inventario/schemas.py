from datetime import date

from pydantic import BaseModel, Field


class EntradaIn(BaseModel):
    producto_id: int
    numero_lote: str = Field(min_length=1, max_length=40)
    cantidad: int = Field(gt=0)
    fecha_vencimiento: date


class SalidaIn(BaseModel):
    producto_id: int
    cantidad: int = Field(gt=0)
