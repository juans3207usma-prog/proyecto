from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app import models  # noqa: F401  (registra todas las tablas)
from app.alertas import router as alertas
from app.catalogo import router_categorias, router_productos
from app.compartido.errores import ErrorNegocio
from app.inventario import router as inventario

app = FastAPI(title="Inventario Farmacia")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router_categorias.router)
app.include_router(router_productos.router)
app.include_router(inventario.router)
app.include_router(alertas.router)


@app.exception_handler(ErrorNegocio)
async def manejar_error_negocio(request: Request, exc: ErrorNegocio):
    return JSONResponse(status_code=exc.status, content={"detail": str(exc)})


@app.get("/health", tags=["salud"])
def health():
    return {"status": "ok"}
