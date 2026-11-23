from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.services import alertas

router = APIRouter(prefix="/alertas", tags=["alertas"])


@router.get("/stock-bajo")
def stock_bajo(db: Session = Depends(get_db)):
    return alertas.stock_bajo(db)


@router.get("/por-vencer")
def por_vencer(dias: int = Query(30, ge=1, le=365), db: Session = Depends(get_db)):
    return alertas.por_vencer(db, dias)
