"""Consultas de lotes. No confirma transacciones: eso lo decide el servicio."""

from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.modulos.inventario.datos.modelos import Lote


def lotes_vendibles_bloqueados(db: Session, producto_id: int, hoy: date) -> list[Lote]:
    """Lotes con stock y sin vencer, bloqueados ante ventas simultaneas."""
    consulta = (
        select(Lote)
        .where(
            Lote.producto_id == producto_id,
            Lote.cantidad > 0,
            Lote.fecha_vencimiento >= hoy,
        )
        .with_for_update()
    )
    return list(db.scalars(consulta))


def stock_vendible(db: Session, producto_ids: list[int], hoy: date) -> dict[int, int]:
    filas = db.execute(
        select(Lote.producto_id, func.sum(Lote.cantidad))
        .where(Lote.producto_id.in_(producto_ids), Lote.fecha_vencimiento >= hoy)
        .group_by(Lote.producto_id)
    ).all()
    return {producto_id: int(total) for producto_id, total in filas}
