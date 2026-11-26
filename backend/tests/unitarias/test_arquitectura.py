"""Hace cumplir las reglas de dependencia: si alguien las rompe, la prueba falla."""

import ast
from pathlib import Path

import pytest

APP = Path(__file__).resolve().parents[2] / "app"
MODULOS = APP / "modulos"


def importaciones(archivo: Path) -> set[str]:
    nombres: set[str] = set()
    for nodo in ast.walk(ast.parse(archivo.read_text(encoding="utf-8"))):
        if isinstance(nodo, ast.Import):
            nombres.update(alias.name for alias in nodo.names)
        elif isinstance(nodo, ast.ImportFrom) and nodo.module:
            nombres.update(f"{nodo.module}.{alias.name}" for alias in nodo.names)
    return nombres


def violaciones(patron: str, prohibido, raiz: Path = MODULOS) -> list[str]:
    archivos = list(raiz.glob(patron))
    assert archivos, f"El patron {patron!r} no encontro archivos"
    return [
        f"{archivo.relative_to(APP)} importa {nombre}"
        for archivo in archivos
        for nombre in importaciones(archivo)
        if prohibido(nombre)
    ]


def empieza_por(*prefijos):
    return lambda nombre: nombre.startswith(prefijos)


def test_el_dominio_es_python_puro():
    prohibido = empieza_por("sqlalchemy", "fastapi", "pydantic", "app.compartido.database")
    assert violaciones("*/dominio/*.py", prohibido) == []


def test_los_servicios_no_conocen_http():
    def prohibido(nombre):
        return nombre.startswith("fastapi") or ".api." in nombre

    assert violaciones("*/servicios/*.py", prohibido) == []


def test_solo_la_unidad_de_trabajo_confirma_transacciones():
    directas = [
        f"{archivo.relative_to(APP)}:{nodo.lineno}"
        for archivo in MODULOS.rglob("*.py")
        for nodo in ast.walk(ast.parse(archivo.read_text(encoding="utf-8")))
        if isinstance(nodo, ast.Attribute) and nodo.attr in {"commit", "rollback"}
    ]
    assert directas == [], "Usa `with transaccion(db):` en lugar de commit/rollback"


def test_la_api_no_accede_a_los_datos_directamente():
    assert violaciones("*/api/*.py", lambda nombre: ".datos." in nombre) == []


def test_los_datos_no_dependen_de_capas_superiores():
    def prohibido(nombre):
        return ".api." in nombre or ".servicios." in nombre

    assert violaciones("*/datos/*.py", prohibido) == []


def test_compartido_no_depende_de_los_modulos():
    prohibido = empieza_por("app.modulos")
    assert violaciones("compartido/*.py", prohibido, raiz=APP) == []


@pytest.mark.parametrize(
    ("patron", "modulos_prohibidos"),
    [
        ("catalogo/servicios/*.py", ("inventario", "alertas")),
        ("catalogo/datos/*.py", ("inventario", "alertas")),
        ("inventario/**/*.py", ("alertas",)),
    ],
)
def test_las_dependencias_entre_modulos_van_en_un_sentido(patron, modulos_prohibidos):
    prohibido = empieza_por(*(f"app.modulos.{m}" for m in modulos_prohibidos))
    assert violaciones(patron, prohibido) == []
