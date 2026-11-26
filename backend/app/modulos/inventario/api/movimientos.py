from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.compartido.database import get_db
from app.modulos.inventario.api.esquemas import EntradaIn, SalidaIn
from app.modulos.inventario.servicios import movimientos as servicio

router = APIRouter(prefix="/movimientos", tags=["movimientos"])


@router.post("/entrada", status_code=201)
def entrada(datos: EntradaIn, db: Session = Depends(get_db)):
    servicio.registrar_entrada(db, **datos.model_dump())
    return {"ok": True}


@router.post("/salida", status_code=201)
def salida(datos: SalidaIn, db: Session = Depends(get_db)):
    servicio.registrar_salida(db, **datos.model_dump())
    return {"ok": True}
