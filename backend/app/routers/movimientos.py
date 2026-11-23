from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import EntradaIn, SalidaIn
from app.services import movimientos

router = APIRouter(prefix="/movimientos", tags=["movimientos"])


@router.post("/entrada", status_code=201)
def entrada(datos: EntradaIn, db: Session = Depends(get_db)):
    movimientos.registrar_entrada(db, **datos.model_dump())
    return {"ok": True}


@router.post("/salida", status_code=201)
def salida(datos: SalidaIn, db: Session = Depends(get_db)):
    movimientos.registrar_salida(db, **datos.model_dump())
    return {"ok": True}
