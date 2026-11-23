from decimal import Decimal

import pytest

from app.catalogo import categorias_service as categorias
from app.catalogo import productos_service as productos
from app.catalogo.schemas import ProductoIn
from app.compartido.errores import Conflicto, NoEncontrado
from app.inventario.stock import stock_por_producto


def datos_producto(categoria_id, **extra):
    base = {
        "nombre": "Aspirina",
        "precio": Decimal("1.50"),
        "stock_minimo": 5,
        "categoria_id": categoria_id,
    }
    return ProductoIn(**{**base, **extra})


def test_categoria_duplicada_se_rechaza(db):
    categorias.crear(db, "Higiene")
    with pytest.raises(Conflicto):
        categorias.crear(db, "Higiene")


def test_categoria_actualizar_y_listar(db):
    cat = categorias.crear(db, "Higiene")
    categorias.actualizar(db, cat.id, "Cuidado personal")
    assert [c.nombre for c in categorias.listar(db)] == ["Cuidado personal"]


def test_categoria_actualizar_a_nombre_existente_falla(db):
    categorias.crear(db, "Higiene")
    otra = categorias.crear(db, "Vitaminas")
    with pytest.raises(Conflicto):
        categorias.actualizar(db, otra.id, "Higiene")


def test_categoria_con_productos_no_se_borra(db, producto):
    with pytest.raises(Conflicto):
        categorias.eliminar(db, producto.categoria_id)


def test_categoria_vacia_se_borra(db):
    cat = categorias.crear(db, "Vacia")
    categorias.eliminar(db, cat.id)
    assert categorias.listar(db) == []


def test_categoria_inexistente(db):
    with pytest.raises(NoEncontrado):
        categorias.eliminar(db, 999)
    with pytest.raises(NoEncontrado):
        categorias.actualizar(db, 999, "X")


def test_crear_producto_con_categoria_inexistente(db):
    with pytest.raises(NoEncontrado):
        productos.crear(db, datos_producto(999))


def test_crear_listar_y_stock(db, producto):
    nuevo = productos.crear(db, datos_producto(producto.categoria_id))
    lista = productos.listar(db)
    stock = stock_por_producto(db, [p.id for p in lista])
    assert {p.nombre: stock.get(p.id, 0) for p in lista} == {"Aspirina": 0, "Paracetamol": 80}
    assert stock_por_producto(db, []) == {}
    assert productos.obtener(db, nuevo.id).nombre == "Aspirina"


def test_actualizar_producto(db, producto):
    productos.actualizar(db, producto.id, datos_producto(producto.categoria_id, nombre="Otro"))
    assert productos.obtener(db, producto.id).nombre == "Otro"


def test_desactivar_producto_es_borrado_logico(db, producto):
    productos.desactivar(db, producto.id)
    assert productos.listar(db) == []
    with pytest.raises(NoEncontrado):
        productos.obtener(db, producto.id)
