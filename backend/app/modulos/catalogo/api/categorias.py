from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from app.compartido.database import get_db
from app.modulos.catalogo.api.esquemas import CategoriaIn, CategoriaOut
from app.modulos.catalogo.servicios import categorias as servicio

router = APIRouter(prefix="/categorias", tags=["categorias"])


@router.get("", response_model=list[CategoriaOut])
def listar(db: Session = Depends(get_db)):
    return servicio.listar(db)


@router.post("", response_model=CategoriaOut, status_code=201)
def crear(datos: CategoriaIn, db: Session = Depends(get_db)):
    return servicio.crear(db, datos.nombre)


@router.put("/{categoria_id}", response_model=CategoriaOut)
def actualizar(categoria_id: int, datos: CategoriaIn, db: Session = Depends(get_db)):
    return servicio.actualizar(db, categoria_id, datos.nombre)


@router.delete("/{categoria_id}", status_code=204)
def eliminar(categoria_id: int, db: Session = Depends(get_db)):
    servicio.eliminar(db, categoria_id)
    return Response(status_code=204)
