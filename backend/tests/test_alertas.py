from datetime import date, timedelta

from app.services.alertas import por_vencer, stock_bajo
from app.services.movimientos import registrar_salida


def test_sin_alerta_si_stock_sobre_el_minimo(db, producto):
    assert stock_bajo(db) == []  # 80 >= 40


def test_alerta_aparece_al_bajar_del_minimo(db, producto):
    registrar_salida(db, producto.id, 50)  # quedan 30 < 40
    alertas = stock_bajo(db)
    assert len(alertas) == 1
    assert alertas[0]["nombre"] == "Paracetamol"
    assert alertas[0]["stock"] == 30


def test_producto_sin_lotes_tambien_alerta(db, producto):
    registrar_salida(db, producto.id, 80)
    assert stock_bajo(db)[0]["stock"] == 0


def test_producto_inactivo_no_alerta(db, producto):
    producto.activo = False
    db.commit()
    assert stock_bajo(db) == []


def test_por_vencer_lista_solo_lotes_en_ventana(db, producto):
    lotes = por_vencer(db, dias=30)
    assert [lote["numero_lote"] for lote in lotes] == ["B"]  # B vence en 20 dias
    assert lotes[0]["fecha_vencimiento"] == (date.today() + timedelta(days=20)).isoformat()
    assert por_vencer(db, dias=10) == []
