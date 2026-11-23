from sqlalchemy import select
from sqlalchemy.orm import Session

from app.catalogo.models import Categoria
from app.compartido.errores import Conflicto, NoEncontrado


def listar(db: Session) -> list[Categoria]:
    return list(db.scalars(select(Categoria).order_by(Categoria.nombre)))


def crear(db: Session, nombre: str) -> Categoria:
    nombre = nombre.strip()
    if db.scalar(select(Categoria).where(Categoria.nombre == nombre)):
        raise Conflicto("La categoria ya existe")
    categoria = Categoria(nombre=nombre)
    db.add(categoria)
    db.commit()
    return categoria


def actualizar(db: Session, categoria_id: int, nombre: str) -> Categoria:
    categoria = db.get(Categoria, categoria_id)
    if not categoria:
        raise NoEncontrado("Categoria no encontrada")
    nombre = nombre.strip()
    otra = db.scalar(
        select(Categoria).where(Categoria.nombre == nombre, Categoria.id != categoria_id)
    )
    if otra:
        raise Conflicto("La categoria ya existe")
    categoria.nombre = nombre
    db.commit()
    return categoria


def eliminar(db: Session, categoria_id: int) -> None:
    categoria = db.get(Categoria, categoria_id)
    if not categoria:
        raise NoEncontrado("Categoria no encontrada")
    if categoria.productos:
        raise Conflicto("No se puede borrar: la categoria tiene productos")
    db.delete(categoria)
    db.commit()
