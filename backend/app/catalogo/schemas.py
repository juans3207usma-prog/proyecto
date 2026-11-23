from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class CategoriaIn(BaseModel):
    nombre: str = Field(min_length=2, max_length=80)


class CategoriaOut(CategoriaIn):
    model_config = ConfigDict(from_attributes=True)
    id: int


class ProductoIn(BaseModel):
    nombre: str = Field(min_length=2, max_length=120)
    precio: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
    stock_minimo: int = Field(ge=0)
    requiere_receta: bool = False
    categoria_id: int


class ProductoOut(ProductoIn):
    model_config = ConfigDict(from_attributes=True)
    id: int
    activo: bool
    stock: int = 0
