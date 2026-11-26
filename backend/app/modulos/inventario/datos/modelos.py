from datetime import UTC, date, datetime

from sqlalchemy import CheckConstraint, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.compartido.database import Base
from app.modulos.catalogo.datos.modelos import Producto


def _ahora() -> datetime:
    return datetime.now(UTC)


class Lote(Base):
    __tablename__ = "lotes"
    __table_args__ = (CheckConstraint("cantidad >= 0", name="ck_lote_cantidad"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    producto_id: Mapped[int] = mapped_column(ForeignKey("productos.id"))
    numero_lote: Mapped[str] = mapped_column(String(40))
    cantidad: Mapped[int]
    fecha_vencimiento: Mapped[date] = mapped_column(index=True)

    # Direccion unica de dependencia: inventario -> catalogo.
    producto: Mapped[Producto] = relationship()


class Movimiento(Base):
    """Historial inmutable: solo se inserta, nunca se edita ni se borra."""

    __tablename__ = "movimientos"

    id: Mapped[int] = mapped_column(primary_key=True)
    producto_id: Mapped[int] = mapped_column(ForeignKey("productos.id"))
    tipo: Mapped[str] = mapped_column(String(10))  # entrada | salida | ajuste
    cantidad: Mapped[int]
    motivo: Mapped[str | None] = mapped_column(String(200))
    creado_en: Mapped[datetime] = mapped_column(default=_ahora)
