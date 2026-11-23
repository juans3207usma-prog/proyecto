from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.alertas import service
from app.compartido.database import get_db

router = APIRouter(prefix="/alertas", tags=["alertas"])


@router.get("/stock-bajo")
def stock_bajo(db: Session = Depends(get_db)):
    return service.stock_bajo(db)


@router.get("/por-vencer")
def por_vencer(dias: int = Query(30, ge=1, le=365), db: Session = Depends(get_db)):
    return service.por_vencer(db, dias)
