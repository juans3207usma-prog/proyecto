"""Pruebas de integracion: flujo completo a traves de la API HTTP."""

from datetime import date, timedelta


def test_flujo_completo(client):
    # categoria -> producto
    cat = client.post("/categorias", json={"nombre": "Analgesicos"})
    assert cat.status_code == 201
    prod = client.post(
        "/productos",
        json={"nombre": "Paracetamol", "precio": "2.50", "stock_minimo": 40,
              "categoria_id": cat.json()["id"]},
    )
    assert prod.status_code == 201
    pid = prod.json()["id"]

    # entrada de lote
    vence = (date.today() + timedelta(days=100)).isoformat()
    ok = client.post(
        "/movimientos/entrada",
        json={
            "producto_id": pid,
            "numero_lote": "L1",
            "cantidad": 50,
            "fecha_vencimiento": vence,
        },
    )
    assert ok.status_code == 201
    assert client.get(f"/productos/{pid}").json()["stock"] == 50

    # salida que deja el stock bajo el minimo -> aparece la alerta
    salida = client.post("/movimientos/salida", json={"producto_id": pid, "cantidad": 20})
    assert salida.status_code == 201
    alertas = client.get("/alertas/stock-bajo").json()
    assert alertas[0]["nombre"] == "Paracetamol"
    assert alertas[0]["stock"] == 30


def test_salida_con_stock_insuficiente_devuelve_409(client, producto):
    r = client.post("/movimientos/salida", json={"producto_id": producto.id, "cantidad": 999})
    assert r.status_code == 409
    assert r.json()["detail"] == "Stock insuficiente"


def test_validaciones_devuelven_422(client, producto):
    r = client.post(
        "/productos",
        json={"nombre": "X", "precio": "-1", "stock_minimo": -2,
              "categoria_id": producto.categoria_id},
    )
    assert r.status_code == 422
    r = client.post("/movimientos/salida", json={"producto_id": producto.id, "cantidad": 0})
    assert r.status_code == 422


def test_404_producto_inexistente(client):
    assert client.get("/productos/999").status_code == 404


def test_categoria_duplicada_409_y_borrado(client):
    assert client.post("/categorias", json={"nombre": "Higiene"}).status_code == 201
    assert client.post("/categorias", json={"nombre": "Higiene"}).status_code == 409
    cid = client.get("/categorias").json()[0]["id"]
    assert client.put(f"/categorias/{cid}", json={"nombre": "Cuidado"}).status_code == 200
    assert client.delete(f"/categorias/{cid}").status_code == 204


def test_producto_put_delete_y_por_vencer(client, producto):
    pid = producto.id
    cuerpo = {"nombre": "Paracetamol XR", "precio": "3.00", "stock_minimo": 10,
              "categoria_id": producto.categoria_id}
    assert client.put(f"/productos/{pid}", json=cuerpo).json()["nombre"] == "Paracetamol XR"
    assert client.get("/alertas/por-vencer?dias=30").json()[0]["numero_lote"] == "B"
    assert client.delete(f"/productos/{pid}").status_code == 204
    assert client.get("/productos").json() == []
    assert client.get("/health").json() == {"status": "ok"}
