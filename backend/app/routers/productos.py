from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import ProductoIn, ProductoOut
from app.services import productos

router = APIRouter(prefix="/productos", tags=["productos"])


def _salida(producto, stock: int) -> ProductoOut:
    return ProductoOut.model_validate(producto).model_copy(update={"stock": stock})


@router.get("", response_model=list[ProductoOut])
def listar(db: Session = Depends(get_db)):
    return [_salida(p, s) for p, s in productos.listar(db)]


@router.get("/{producto_id}", response_model=ProductoOut)
def obtener(producto_id: int, db: Session = Depends(get_db)):
    producto = productos.obtener(db, producto_id)
    return _salida(producto, productos.stock_actual(db, producto_id))


@router.post("", response_model=ProductoOut, status_code=201)
def crear(datos: ProductoIn, db: Session = Depends(get_db)):
    producto = productos.crear(db, datos)
    return _salida(producto, 0)


@router.put("/{producto_id}", response_model=ProductoOut)
def actualizar(producto_id: int, datos: ProductoIn, db: Session = Depends(get_db)):
    producto = productos.actualizar(db, producto_id, datos)
    return _salida(producto, productos.stock_actual(db, producto_id))


@router.delete("/{producto_id}", status_code=204)
def desactivar(producto_id: int, db: Session = Depends(get_db)):
    productos.desactivar(db, producto_id)
    return Response(status_code=204)
