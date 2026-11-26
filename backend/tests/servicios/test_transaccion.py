import pytest

from app.compartido.transaccion import transaccion
from app.models import Categoria


def test_confirma_al_terminar_el_bloque(db):
    with transaccion(db):
        db.add(Categoria(nombre="Higiene"))
    db.rollback()  # no deshace nada: ya estaba confirmado
    assert db.query(Categoria).count() == 1


def test_revierte_todo_y_relanza_el_error(db):
    with pytest.raises(RuntimeError), transaccion(db):
        db.add(Categoria(nombre="Higiene"))
        db.flush()  # ya enviado a la BD, pero sin confirmar
        raise RuntimeError("fallo a mitad del caso de uso")
    assert db.query(Categoria).count() == 0


def test_una_salida_que_falla_al_registrar_no_descuenta_stock(db, producto, monkeypatch):
    from app.modulos.inventario.servicios import movimientos

    def movimiento_roto(**_):
        raise RuntimeError("no se pudo registrar el movimiento")

    monkeypatch.setattr(movimientos, "Movimiento", movimiento_roto)
    with pytest.raises(RuntimeError):
        movimientos.registrar_salida(db, producto.id, 40)

    from app.modulos.inventario.servicios.stock import stock_por_producto

    assert stock_por_producto(db, [producto.id]) == {producto.id: 80}
