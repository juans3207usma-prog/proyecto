from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.catalogo.models import Producto
from app.compartido.errores import NoEncontrado
from app.inventario.fefo import LoteStock, planificar_salida
from app.inventario.models import Lote, Movimiento


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
    """Descuenta stock aplicando el plan FEFO dentro de una sola transaccion.

    La decision (que lote, cuanto) la toma `fefo.planificar_salida`; aqui solo se
    bloquean las filas, se aplica el plan y se registra el movimiento. Si el stock
    no alcanza o algo falla, se hace rollback y ningun lote cambia.
    """
    _producto_activo(db, producto_id)
    try:
        lotes = db.scalars(
            select(Lote)
            .where(
                Lote.producto_id == producto_id,
                Lote.cantidad > 0,
                Lote.fecha_vencimiento >= date.today(),
            )
            .with_for_update()  # bloquea las filas ante ventas simultaneas
        ).all()

        plan = planificar_salida(
            [LoteStock(lote.id, lote.cantidad, lote.fecha_vencimiento) for lote in lotes],
            cantidad,
            date.today(),
        )
        for lote in lotes:
            lote.cantidad -= plan.get(lote.id, 0)

        db.add(Movimiento(producto_id=producto_id, tipo="salida", cantidad=cantidad))
        db.commit()
    except Exception:
        db.rollback()
        raise
