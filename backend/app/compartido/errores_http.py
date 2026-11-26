"""Traduce los errores de negocio a respuestas HTTP en un solo lugar."""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.compartido.errores import ErrorNegocio


async def _manejar_error_negocio(request: Request, exc: ErrorNegocio) -> JSONResponse:
    return JSONResponse(status_code=exc.status, content={"detail": str(exc)})


def registrar_manejadores(app: FastAPI) -> None:
    app.add_exception_handler(ErrorNegocio, _manejar_error_negocio)
