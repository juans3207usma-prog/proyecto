"""Pruebas de la regla FEFO pura: sin base de datos ni framework."""

from datetime import date, timedelta

import pytest

from app.compartido.errores import StockInsuficiente
from app.inventario.fefo import LoteStock, planificar_salida

HOY = date(2026, 1, 1)


def lote(id_, cantidad, dias):
    return LoteStock(id_, cantidad, HOY + timedelta(days=dias))


def test_consume_primero_el_que_vence_antes():
    lotes = [lote(1, 50, 300), lote(2, 30, 20)]  # el 2 vence antes aunque llego despues
    assert planificar_salida(lotes, 10, HOY) == {2: 10}


def test_cruza_varios_lotes_en_orden():
    lotes = [lote(1, 50, 300), lote(2, 30, 20)]
    assert planificar_salida(lotes, 40, HOY) == {2: 30, 1: 10}


def test_no_toca_lotes_que_no_hacen_falta():
    lotes = [lote(1, 50, 10), lote(2, 50, 20), lote(3, 50, 30)]
    assert planificar_salida(lotes, 50, HOY) == {1: 50}


def test_ignora_lotes_vencidos_y_vacios():
    lotes = [lote(1, 99, -1), lote(2, 0, 5), lote(3, 10, 5)]
    assert planificar_salida(lotes, 10, HOY) == {3: 10}


def test_lote_que_vence_hoy_aun_es_vendible():
    assert planificar_salida([lote(1, 5, 0)], 5, HOY) == {1: 5}


def test_empate_de_fecha_gana_el_menor_id():
    lotes = [lote(7, 10, 5), lote(3, 10, 5)]
    assert planificar_salida(lotes, 5, HOY) == {3: 5}


def test_stock_insuficiente_lanza_error():
    with pytest.raises(StockInsuficiente):
        planificar_salida([lote(1, 10, 5)], 11, HOY)


def test_sin_lotes_lanza_error():
    with pytest.raises(StockInsuficiente):
        planificar_salida([], 1, HOY)
