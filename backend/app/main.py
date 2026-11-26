from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import models  # noqa: F401  (registra todas las tablas)
from app.compartido.config import settings
from app.compartido.errores_http import registrar_manejadores
from app.modulos.alertas.api import alertas
from app.modulos.catalogo.api import categorias, productos
from app.modulos.inventario.api import movimientos

# Para agregar un modulo nuevo basta con sumar su router a esta lista.
ROUTERS = [categorias.router, productos.router, movimientos.router, alertas.router]


def crear_app() -> FastAPI:
    app = FastAPI(title="Inventario Farmacia")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    registrar_manejadores(app)
    for router in ROUTERS:
        app.include_router(router)

    @app.get("/health", tags=["salud"])
    def health():
        return {"status": "ok"}

    return app


app = crear_app()
