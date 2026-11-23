from decimal import Decimal

from sqlalchemy import CheckConstraint, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.compartido.database import Base


class Categoria(Base):
    __tablename__ = "categorias"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(80), unique=True)
    productos: Mapped[list["Producto"]] = relationship(back_populates="categoria")


class Producto(Base):
    """El catalogo no conoce lotes: esa relacion vive solo en `inventario`."""

    __tablename__ = "productos"
    __table_args__ = (
        CheckConstraint("precio > 0", name="ck_producto_precio"),
        CheckConstraint("stock_minimo >= 0", name="ck_producto_stock_minimo"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(120))
    precio: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    stock_minimo: Mapped[int] = mapped_column(default=10)
    requiere_receta: Mapped[bool] = mapped_column(default=False)
    activo: Mapped[bool] = mapped_column(default=True)  # borrado logico
    categoria_id: Mapped[int] = mapped_column(ForeignKey("categorias.id"))

    categoria: Mapped[Categoria] = relationship(back_populates="productos")
