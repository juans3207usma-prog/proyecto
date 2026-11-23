from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import CategoriaIn, CategoriaOut
from app.services import categorias

router = APIRouter(prefix="/categorias", tags=["categorias"])


@router.get("", response_model=list[CategoriaOut])
def listar(db: Session = Depends(get_db)):
    return categorias.listar(db)


@router.post("", response_model=CategoriaOut, status_code=201)
def crear(datos: CategoriaIn, db: Session = Depends(get_db)):
    return categorias.crear(db, datos.nombre)


@router.put("/{categoria_id}", response_model=CategoriaOut)
def actualizar(categoria_id: int, datos: CategoriaIn, db: Session = Depends(get_db)):
    return categorias.actualizar(db, categoria_id, datos.nombre)


@router.delete("/{categoria_id}", status_code=204)
def eliminar(categoria_id: int, db: Session = Depends(get_db)):
    categorias.eliminar(db, categoria_id)
    return Response(status_code=204)
