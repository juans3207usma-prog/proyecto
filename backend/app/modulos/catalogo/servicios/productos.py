"""Casos de uso de productos.

Reciben datos simples (no esquemas HTTP), asi sirven igual desde la API,
un script o una prueba.
"""

from decimal import Decimal

from sqlalchemy.orm import Session

from app.compartido.errores import NoEncontrado
from app.compartido.transaccion import transaccion
from app.modulos.catalogo.datos import repositorio
from app.modulos.catalogo.datos.modelos import Producto


def listar(db: Session) -> list[Producto]:
    return repositorio.listar_productos_activos(db)


def obtener(db: Session, producto_id: int) -> Producto:
    """Devuelve un producto activo. Es la puerta de entrada para otros modulos."""
    producto = repositorio.producto_por_id(db, producto_id)
    if not producto or not producto.activo:
        raise NoEncontrado("Producto no encontrado")
    return producto


def _validar_categoria(db: Session, categoria_id: int) -> None:
    if not repositorio.categoria_por_id(db, categoria_id):
        raise NoEncontrado("Categoria no encontrada")


def crear(
    db: Session,
    *,
    nombre: str,
    precio: Decimal,
    stock_minimo: int,
    categoria_id: int,
    requiere_receta: bool = False,
) -> Producto:
    _validar_categoria(db, categoria_id)
    producto = Producto(
        nombre=nombre,
        precio=precio,
        stock_minimo=stock_minimo,
        categoria_id=categoria_id,
        requiere_receta=requiere_receta,
    )
    with transaccion(db):
        db.add(producto)
    return producto


def actualizar(
    db: Session,
    producto_id: int,
    *,
    nombre: str,
    precio: Decimal,
    stock_minimo: int,
    categoria_id: int,
    requiere_receta: bool = False,
) -> Producto:
    producto = obtener(db, producto_id)
    _validar_categoria(db, categoria_id)
    with transaccion(db):
        producto.nombre = nombre
        producto.precio = precio
        producto.stock_minimo = stock_minimo
        producto.categoria_id = categoria_id
        producto.requiere_receta = requiere_receta
    return producto


def desactivar(db: Session, producto_id: int) -> None:
    """Borrado logico: conserva el historial de movimientos."""
    producto = obtener(db, producto_id)
    with transaccion(db):
        producto.activo = False
