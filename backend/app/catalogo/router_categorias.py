from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from app.catalogo import categorias_service as service
from app.catalogo.schemas import CategoriaIn, CategoriaOut
from app.compartido.database import get_db

router = APIRouter(prefix="/categorias", tags=["categorias"])


@router.get("", response_model=list[CategoriaOut])
def listar(db: Session = Depends(get_db)):
    return service.listar(db)


@router.post("", response_model=CategoriaOut, status_code=201)
def crear(datos: CategoriaIn, db: Session = Depends(get_db)):
    return service.crear(db, datos.nombre)


@router.put("/{categoria_id}", response_model=CategoriaOut)
def actualizar(categoria_id: int, datos: CategoriaIn, db: Session = Depends(get_db)):
    return service.actualizar(db, categoria_id, datos.nombre)


@router.delete("/{categoria_id}", status_code=204)
def eliminar(categoria_id: int, db: Session = Depends(get_db)):
    service.eliminar(db, categoria_id)
    return Response(status_code=204)
