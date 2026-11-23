from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.inventario.models import Lote


def stock_por_producto(db: Session, producto_ids: list[int]) -> dict[int, int]:
    """Stock vendible (lotes no vencidos) de varios productos en una sola consulta."""
    if not producto_ids:
        return {}
    filas = db.execute(
        select(Lote.producto_id, func.sum(Lote.cantidad))
        .where(Lote.producto_id.in_(producto_ids), Lote.fecha_vencimiento >= date.today())
        .group_by(Lote.producto_id)
    ).all()
    return {producto_id: int(total) for producto_id, total in filas}
