from sqlalchemy import select
from sqlalchemy.orm import Session

from app.catalogo.models import Categoria, Producto
from app.catalogo.schemas import ProductoIn
from app.compartido.errores import NoEncontrado


def listar(db: Session) -> list[Producto]:
    return list(db.scalars(select(Producto).where(Producto.activo).order_by(Producto.nombre)))


def obtener(db: Session, producto_id: int) -> Producto:
    producto = db.get(Producto, producto_id)
    if not producto or not producto.activo:
        raise NoEncontrado("Producto no encontrado")
    return producto


def _validar_categoria(db: Session, categoria_id: int) -> None:
    if not db.get(Categoria, categoria_id):
        raise NoEncontrado("Categoria no encontrada")


def crear(db: Session, datos: ProductoIn) -> Producto:
    _validar_categoria(db, datos.categoria_id)
    producto = Producto(**datos.model_dump())
    db.add(producto)
    db.commit()
    return producto


def actualizar(db: Session, producto_id: int, datos: ProductoIn) -> Producto:
    producto = obtener(db, producto_id)
    _validar_categoria(db, datos.categoria_id)
    for campo, valor in datos.model_dump().items():
        setattr(producto, campo, valor)
    db.commit()
    return producto


def desactivar(db: Session, producto_id: int) -> None:
    """Borrado logico: conserva el historial de movimientos."""
    producto = obtener(db, producto_id)
    producto.activo = False
    db.commit()
