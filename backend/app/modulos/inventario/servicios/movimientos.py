from datetime import date

from sqlalchemy.orm import Session

from app.compartido.transaccion import transaccion
from app.modulos.catalogo.servicios import productos
from app.modulos.inventario.datos import repositorio
from app.modulos.inventario.datos.modelos import Lote, Movimiento
from app.modulos.inventario.dominio.fefo import LoteStock, planificar_salida


def registrar_entrada(
    db: Session,
    producto_id: int,
    numero_lote: str,
    cantidad: int,
    fecha_vencimiento: date,
) -> None:
    """Crea el lote y su movimiento en una sola transaccion."""
    productos.obtener(db, producto_id)  # 404 si no existe o esta inactivo
    with transaccion(db):
        db.add(
            Lote(
                producto_id=producto_id,
                numero_lote=numero_lote,
                cantidad=cantidad,
                fecha_vencimiento=fecha_vencimiento,
            )
        )
        db.add(Movimiento(producto_id=producto_id, tipo="entrada", cantidad=cantidad))


def registrar_salida(db: Session, producto_id: int, cantidad: int) -> None:
    """Descuenta stock aplicando el plan FEFO dentro de una sola transaccion.

    La decision (que lote, cuanto) la toma el dominio (`planificar_salida`); aqui
    solo se bloquean las filas, se aplica el plan y se registra el movimiento.
    Si el stock no alcanza o algo falla, se hace rollback y ningun lote cambia.
    """
    productos.obtener(db, producto_id)
    hoy = date.today()
    with transaccion(db):
        lotes = repositorio.lotes_vendibles_bloqueados(db, producto_id, hoy)
        plan = planificar_salida(
            [LoteStock(lote.id, lote.cantidad, lote.fecha_vencimiento) for lote in lotes],
            cantidad,
            hoy,
        )
        for lote in lotes:
            lote.cantidad -= plan.get(lote.id, 0)

        db.add(Movimiento(producto_id=producto_id, tipo="salida", cantidad=cantidad))
