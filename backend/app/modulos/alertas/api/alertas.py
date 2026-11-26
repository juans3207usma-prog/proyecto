from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.compartido.database import get_db
from app.modulos.alertas.api.esquemas import AlertaStockBajo, LotePorVencer
from app.modulos.alertas.servicios import alertas as servicio

router = APIRouter(prefix="/alertas", tags=["alertas"])


@router.get("/stock-bajo", response_model=list[AlertaStockBajo])
def stock_bajo(db: Session = Depends(get_db)):
    return servicio.stock_bajo(db)


@router.get("/por-vencer", response_model=list[LotePorVencer])
def por_vencer(dias: int = Query(30, ge=1, le=365), db: Session = Depends(get_db)):
    return servicio.por_vencer(db, dias)
