from datetime import date

from sqlalchemy.orm import Session

from app.modulos.inventario.datos import repositorio


def stock_por_producto(db: Session, producto_ids: list[int]) -> dict[int, int]:
    """Stock vendible (lotes no vencidos) de varios productos en una sola consulta."""
    if not producto_ids:
        return {}
    return repositorio.stock_vendible(db, producto_ids, date.today())
