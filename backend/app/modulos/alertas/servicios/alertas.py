from datetime import date, timedelta

from sqlalchemy.orm import Session

from app.modulos.alertas.datos import repositorio


def stock_bajo(db: Session) -> list[dict]:
    """Productos activos cuyo stock vendible esta por debajo del minimo."""
    return [
        {
            "producto_id": producto.id,
            "nombre": producto.nombre,
            "stock": stock,
            "stock_minimo": producto.stock_minimo,
        }
        for producto, stock in repositorio.productos_bajo_minimo(db, date.today())
    ]


def por_vencer(db: Session, dias: int = 30) -> list[dict]:
    """Lotes con stock que vencen dentro de `dias` dias."""
    hoy = date.today()
    return [
        {
            "producto_id": lote.producto_id,
            "producto": lote.producto.nombre,
            "numero_lote": lote.numero_lote,
            "cantidad": lote.cantidad,
            "fecha_vencimiento": lote.fecha_vencimiento.isoformat(),
        }
        for lote in repositorio.lotes_por_vencer(db, hoy, hoy + timedelta(days=dias))
    ]
