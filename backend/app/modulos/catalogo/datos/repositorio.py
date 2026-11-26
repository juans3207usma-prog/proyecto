"""Consultas del catalogo. No confirma transacciones: eso lo decide el servicio."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modulos.catalogo.datos.modelos import Categoria, Producto


def listar_categorias(db: Session) -> list[Categoria]:
    return list(db.scalars(select(Categoria).order_by(Categoria.nombre)))


def categoria_por_id(db: Session, categoria_id: int) -> Categoria | None:
    return db.get(Categoria, categoria_id)


def categoria_por_nombre(db: Session, nombre: str) -> Categoria | None:
    return db.scalar(select(Categoria).where(Categoria.nombre == nombre))


def categoria_tiene_productos(db: Session, categoria_id: int) -> bool:
    consulta = select(Producto.id).where(Producto.categoria_id == categoria_id).limit(1)
    return db.scalar(consulta) is not None


def listar_productos_activos(db: Session) -> list[Producto]:
    return list(db.scalars(select(Producto).where(Producto.activo).order_by(Producto.nombre)))


def producto_por_id(db: Session, producto_id: int) -> Producto | None:
    return db.get(Producto, producto_id)
