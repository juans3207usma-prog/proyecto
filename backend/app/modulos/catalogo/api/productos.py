from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from app.compartido.database import get_db
from app.modulos.catalogo.api.esquemas import ProductoIn, ProductoOut
from app.modulos.catalogo.servicios import productos as servicio

# Unica dependencia de lectura hacia `inventario`: mostrar el stock junto al producto.
from app.modulos.inventario.servicios.stock import stock_por_producto

router = APIRouter(prefix="/productos", tags=["productos"])


def _salida(producto, stock: int) -> ProductoOut:
    return ProductoOut.model_validate(producto).model_copy(update={"stock": stock})


def _con_stock(db: Session, producto) -> ProductoOut:
    return _salida(producto, stock_por_producto(db, [producto.id]).get(producto.id, 0))


@router.get("", response_model=list[ProductoOut])
def listar(db: Session = Depends(get_db)):
    productos = servicio.listar(db)
    stock = stock_por_producto(db, [p.id for p in productos])
    return [_salida(p, stock.get(p.id, 0)) for p in productos]


@router.get("/{producto_id}", response_model=ProductoOut)
def obtener(producto_id: int, db: Session = Depends(get_db)):
    return _con_stock(db, servicio.obtener(db, producto_id))


@router.post("", response_model=ProductoOut, status_code=201)
def crear(datos: ProductoIn, db: Session = Depends(get_db)):
    return _salida(servicio.crear(db, **datos.model_dump()), 0)


@router.put("/{producto_id}", response_model=ProductoOut)
def actualizar(producto_id: int, datos: ProductoIn, db: Session = Depends(get_db)):
    return _con_stock(db, servicio.actualizar(db, producto_id, **datos.model_dump()))


@router.delete("/{producto_id}", status_code=204)
def desactivar(producto_id: int, db: Session = Depends(get_db)):
    servicio.desactivar(db, producto_id)
    return Response(status_code=204)
