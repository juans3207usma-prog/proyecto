from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Lote, Movimiento, Producto
from app.services.errores import NoEncontrado, StockInsuficiente


def _producto_activo(db: Session, producto_id: int) -> Producto:
    producto = db.get(Producto, producto_id)
    if not producto or not producto.activo:
        raise NoEncontrado("Producto no encontrado")
    return producto


def registrar_entrada(
    db: Session,
    producto_id: int,
    numero_lote: str,
    cantidad: int,
    fecha_vencimiento: date,
) -> None:
    """Crea el lote y su movimiento en una sola transaccion."""
    _producto_activo(db, producto_id)
    try:
        db.add(
            Lote(
                producto_id=producto_id,
                numero_lote=numero_lote,
                cantidad=cantidad,
                fecha_vencimiento=fecha_vencimiento,
            )
        )
        db.add(Movimiento(producto_id=producto_id, tipo="entrada", cantidad=cantidad))
        db.commit()
    except Exception:
        db.rollback()
        raise


def registrar_salida(db: Session, producto_id: int, cantidad: int) -> None:
    """Descuenta stock con FEFO (primero en vencer, primero en salir).

    Todo ocurre en una transaccion: si el stock no alcanza o algo falla,
    se hace rollback y ningun lote cambia.
    """
    _producto_activo(db, producto_id)
    try:
        lotes = db.scalars(
            select(Lote)
            .where(
                Lote.producto_id == producto_id,
                Lote.cantidad > 0,
                Lote.fecha_vencimiento >= date.today(),  # nunca vender vencidos
            )
            .order_by(Lote.fecha_vencimiento, Lote.id)  # FEFO + desempate estable
            .with_for_update()  # bloquea las filas ante ventas simultaneas
        ).all()

        if sum(lote.cantidad for lote in lotes) < cantidad:
            raise StockInsuficiente("Stock insuficiente")

        pendiente = cantidad
        for lote in lotes:
            if pendiente == 0:
                break
            tomar = min(lote.cantidad, pendiente)
            lote.cantidad -= tomar
            pendiente -= tomar

        db.add(Movimiento(producto_id=producto_id, tipo="salida", cantidad=cantidad))
        db.commit()
    except Exception:
        db.rollback()
        raise
