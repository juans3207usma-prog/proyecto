"""Registro central de modelos: importarlos aqui los deja en `Base.metadata`.

Lo usan Alembic (migraciones), la semilla y las pruebas.
"""

from app.modulos.catalogo.datos.modelos import Categoria, Producto
from app.modulos.inventario.datos.modelos import Lote, Movimiento

__all__ = ["Categoria", "Lote", "Movimiento", "Producto"]
