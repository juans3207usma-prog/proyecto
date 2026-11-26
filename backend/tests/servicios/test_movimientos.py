from datetime import date, timedelta

import pytest

from app.compartido.errores import NoEncontrado, StockInsuficiente
from app.models import Lote, Movimiento
from app.modulos.inventario.servicios.movimientos import registrar_entrada, registrar_salida


def lote(db, nombre):
    return db.query(Lote).filter_by(numero_lote=nombre).one()


def test_salida_de_un_solo_lote(db, producto):
    registrar_salida(db, producto.id, 10)
    assert lote(db, "B").cantidad == 20  # B vence antes: sale de ahi
    assert lote(db, "A").cantidad == 50


def test_salida_cruza_lotes_en_orden_fefo(db, producto):
    registrar_salida(db, producto.id, 40)
    assert lote(db, "B").cantidad == 0  # vencia antes: se agota primero
    assert lote(db, "A").cantidad == 40  # el resto sale del siguiente


def test_stock_insuficiente_no_cambia_nada(db, producto):
    with pytest.raises(StockInsuficiente):
        registrar_salida(db, producto.id, 999)
    assert lote(db, "A").cantidad == 50
    assert lote(db, "B").cantidad == 30
    assert db.query(Movimiento).count() == 0  # rollback: sin movimiento fantasma


def test_no_vende_lotes_vencidos(db, producto):
    lote(db, "B").fecha_vencimiento = date.today() - timedelta(days=1)
    db.commit()
    with pytest.raises(StockInsuficiente):
        registrar_salida(db, producto.id, 60)  # solo 50 son vendibles
    registrar_salida(db, producto.id, 50)
    assert lote(db, "B").cantidad == 30  # el vencido no se toca


def test_empate_de_fechas_se_desempata_por_id(db, producto):
    fecha = date.today() + timedelta(days=20)
    lote(db, "A").fecha_vencimiento = fecha
    db.commit()
    registrar_salida(db, producto.id, 10)
    assert lote(db, "A").cantidad == 40  # A tiene id menor que B


def test_salida_registra_movimiento(db, producto):
    registrar_salida(db, producto.id, 5)
    mov = db.query(Movimiento).one()
    assert (mov.tipo, mov.cantidad) == ("salida", 5)


def test_entrada_crea_lote_y_movimiento(db, producto):
    registrar_entrada(db, producto.id, "C", 25, date.today() + timedelta(days=90))
    assert lote(db, "C").cantidad == 25
    assert db.query(Movimiento).filter_by(tipo="entrada").count() == 1


def test_producto_inexistente(db):
    with pytest.raises(NoEncontrado):
        registrar_salida(db, 999, 1)
    with pytest.raises(NoEncontrado):
        registrar_entrada(db, 999, "X", 1, date.today())
