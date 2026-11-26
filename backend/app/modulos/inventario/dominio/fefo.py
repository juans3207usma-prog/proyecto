"""Dominio: regla FEFO (primero en vencer, primero en salir) como funcion pura.

No usa base de datos ni framework: recibe datos y devuelve un plan. Por eso se
prueba de forma directa y rapida, y el servicio solo se encarga de aplicar el plan.
"""

from dataclasses import dataclass
from datetime import date

from app.compartido.errores import StockInsuficiente


@dataclass(frozen=True)
class LoteStock:
    id: int
    cantidad: int
    fecha_vencimiento: date


def planificar_salida(lotes: list[LoteStock], cantidad: int, hoy: date) -> dict[int, int]:
    """Devuelve {id_lote: unidades a descontar} para cubrir `cantidad`.

    - Ignora lotes vacios y lotes ya vencidos.
    - Consume primero el lote que vence antes; ante empate de fecha, el de menor id.
    - Lanza StockInsuficiente si lo vendible no alcanza (no devuelve planes parciales).
    """
    vendibles = sorted(
        (lote for lote in lotes if lote.cantidad > 0 and lote.fecha_vencimiento >= hoy),
        key=lambda lote: (lote.fecha_vencimiento, lote.id),
    )
    if sum(lote.cantidad for lote in vendibles) < cantidad:
        raise StockInsuficiente("Stock insuficiente")

    plan: dict[int, int] = {}
    pendiente = cantidad
    for lote in vendibles:
        if pendiente == 0:
            break
        tomar = min(lote.cantidad, pendiente)
        plan[lote.id] = tomar
        pendiente -= tomar
    return plan
