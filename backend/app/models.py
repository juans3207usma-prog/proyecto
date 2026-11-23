from datetime import UTC, date, datetime
from decimal import Decimal

from sqlalchemy import CheckConstraint, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def _ahora() -> datetime:
    return datetime.now(UTC)


class Categoria(Base):
    __tablename__ = "categorias"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(80), unique=True)
    productos: Mapped[list["Producto"]] = relationship(back_populates="categoria")


class Producto(Base):
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
    lotes: Mapped[list["Lote"]] = relationship(back_populates="producto")


class Lote(Base):
    __tablename__ = "lotes"
    __table_args__ = (CheckConstraint("cantidad >= 0", name="ck_lote_cantidad"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    producto_id: Mapped[int] = mapped_column(ForeignKey("productos.id"))
    numero_lote: Mapped[str] = mapped_column(String(40))
    cantidad: Mapped[int]
    fecha_vencimiento: Mapped[date] = mapped_column(index=True)

    producto: Mapped[Producto] = relationship(back_populates="lotes")


class Movimiento(Base):
    """Historial inmutable: solo se inserta, nunca se edita ni se borra."""

    __tablename__ = "movimientos"

    id: Mapped[int] = mapped_column(primary_key=True)
    producto_id: Mapped[int] = mapped_column(ForeignKey("productos.id"))
    tipo: Mapped[str] = mapped_column(String(10))  # entrada | salida | ajuste
    cantidad: Mapped[int]
    motivo: Mapped[str | None] = mapped_column(String(200))
    creado_en: Mapped[datetime] = mapped_column(default=_ahora)
