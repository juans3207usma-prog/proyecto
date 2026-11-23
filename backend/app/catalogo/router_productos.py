from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from app.catalogo import productos_service as service
from app.catalogo.models import Producto
from app.catalogo.schemas import ProductoIn, ProductoOut
from app.compartido.database import get_db

# Unica dependencia de lectura hacia `inventario`: mostrar el stock junto al producto.
from app.inventario.stock import stock_por_producto

router = APIRouter(prefix="/productos", tags=["productos"])


def _salida(producto: Producto, stock: int) -> ProductoOut:
    return ProductoOut.model_validate(producto).model_copy(update={"stock": stock})


@router.get("", response_model=list[ProductoOut])
def listar(db: Session = Depends(get_db)):
    productos = service.listar(db)
    stock = stock_por_producto(db, [p.id for p in productos])
    return [_salida(p, stock.get(p.id, 0)) for p in productos]


@router.get("/{producto_id}", response_model=ProductoOut)
def obtener(producto_id: int, db: Session = Depends(get_db)):
    producto = service.obtener(db, producto_id)
    return _salida(producto, stock_por_producto(db, [producto_id]).get(producto_id, 0))


@router.post("", response_model=ProductoOut, status_code=201)
def crear(datos: ProductoIn, db: Session = Depends(get_db)):
    return _salida(service.crear(db, datos), 0)


@router.put("/{producto_id}", response_model=ProductoOut)
def actualizar(producto_id: int, datos: ProductoIn, db: Session = Depends(get_db)):
    producto = service.actualizar(db, producto_id, datos)
    return _salida(producto, stock_por_producto(db, [producto_id]).get(producto_id, 0))


@router.delete("/{producto_id}", status_code=204)
def desactivar(producto_id: int, db: Session = Depends(get_db)):
    service.desactivar(db, producto_id)
    return Response(status_code=204)
