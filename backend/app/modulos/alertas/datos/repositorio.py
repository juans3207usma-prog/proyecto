"""Consultas de solo lectura que cruzan catalogo e inventario."""

from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import Session, contains_eager

from app.modulos.catalogo.datos.modelos import Producto
from app.modulos.inventario.datos.modelos import Lote


def productos_bajo_minimo(db: Session, hoy: date) -> list[tuple[Producto, int]]:
    stock = func.coalesce(func.sum(Lote.cantidad), 0)
    filas = db.execute(
        select(Producto, stock.label("stock"))
        .outerjoin(Lote, (Lote.producto_id == Producto.id) & (Lote.fecha_vencimiento >= hoy))
        .where(Producto.activo)
        .group_by(Producto.id)
        .having(stock < Producto.stock_minimo)
        .order_by(Producto.nombre)
    ).all()
    return [(producto, int(total)) for producto, total in filas]


def lotes_por_vencer(db: Session, desde: date, hasta: date) -> list[Lote]:
    """Trae el producto en la misma consulta para evitar una consulta por lote."""
    consulta = (
        select(Lote)
        .join(Lote.producto)
        .options(contains_eager(Lote.producto))
        .where(
            Producto.activo,
            Lote.cantidad > 0,
            Lote.fecha_vencimiento.between(desde, hasta),
        )
        .order_by(Lote.fecha_vencimiento)
    )
    return list(db.scalars(consulta))
