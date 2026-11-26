from sqlalchemy.orm import Session

from app.compartido.errores import Conflicto, NoEncontrado
from app.compartido.transaccion import transaccion
from app.modulos.catalogo.datos import repositorio
from app.modulos.catalogo.datos.modelos import Categoria


def listar(db: Session) -> list[Categoria]:
    return repositorio.listar_categorias(db)


def _obtener(db: Session, categoria_id: int) -> Categoria:
    categoria = repositorio.categoria_por_id(db, categoria_id)
    if not categoria:
        raise NoEncontrado("Categoria no encontrada")
    return categoria


def crear(db: Session, nombre: str) -> Categoria:
    nombre = nombre.strip()
    if repositorio.categoria_por_nombre(db, nombre):
        raise Conflicto("La categoria ya existe")
    categoria = Categoria(nombre=nombre)
    with transaccion(db):
        db.add(categoria)
    return categoria


def actualizar(db: Session, categoria_id: int, nombre: str) -> Categoria:
    categoria = _obtener(db, categoria_id)
    nombre = nombre.strip()
    existente = repositorio.categoria_por_nombre(db, nombre)
    if existente and existente.id != categoria_id:
        raise Conflicto("La categoria ya existe")
    with transaccion(db):
        categoria.nombre = nombre
    return categoria


def eliminar(db: Session, categoria_id: int) -> None:
    categoria = _obtener(db, categoria_id)
    if repositorio.categoria_tiene_productos(db, categoria_id):
        raise Conflicto("No se puede borrar: la categoria tiene productos")
    with transaccion(db):
        db.delete(categoria)
