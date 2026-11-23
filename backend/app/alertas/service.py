from datetime import date, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.catalogo.models import Producto
from app.inventario.models import Lote


def stock_bajo(db: Session) -> list[dict]:
    """Productos activos cuyo stock vendible esta por debajo del minimo."""
    stock = func.coalesce(func.sum(Lote.cantidad), 0)
    filas = db.execute(
        select(Producto, stock.label("stock"))
        .outerjoin(
            Lote,
            (Lote.producto_id == Producto.id) & (Lote.fecha_vencimiento >= date.today()),
        )
        .where(Producto.activo)
        .group_by(Producto.id)
        .having(stock < Producto.stock_minimo)
        .order_by(Producto.nombre)
    ).all()
    return [
        {
            "producto_id": p.id,
            "nombre": p.nombre,
            "stock": int(s),
            "stock_minimo": p.stock_minimo,
        }
        for p, s in filas
    ]


def por_vencer(db: Session, dias: int = 30) -> list[dict]:
    """Lotes con stock que vencen dentro de `dias` dias."""
    hoy = date.today()
    lotes = db.scalars(
        select(Lote)
        .join(Producto)
        .where(
            Producto.activo,
            Lote.cantidad > 0,
            Lote.fecha_vencimiento.between(hoy, hoy + timedelta(days=dias)),
        )
        .order_by(Lote.fecha_vencimiento)
    ).all()
    return [
        {
            "producto_id": lote.producto_id,
            "producto": lote.producto.nombre,
            "numero_lote": lote.numero_lote,
            "cantidad": lote.cantidad,
            "fecha_vencimiento": lote.fecha_vencimiento.isoformat(),
        }
        for lote in lotes
    ]
