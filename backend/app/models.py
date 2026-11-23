"""Registro central de modelos: importarlos aqui los deja en `Base.metadata`.

Lo usan Alembic (migraciones) y las pruebas para crear todas las tablas.
"""

from app.catalogo.models import Categoria, Producto
from app.inventario.models import Lote, Movimiento

__all__ = ["Categoria", "Lote", "Movimiento", "Producto"]
