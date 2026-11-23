"""Datos semilla idempotentes: se puede ejecutar varias veces sin duplicar."""

from datetime import date, timedelta
from decimal import Decimal

from sqlalchemy import select

from app.database import SessionLocal
from app.models import Categoria, Lote, Producto

CATEGORIAS = ["Analgesicos", "Antibioticos", "Higiene", "Suplementos"]

# nombre, categoria, precio, stock minimo, receta, [(lote, cantidad, dias a vencer)]
PRODUCTOS = [
    (
        "Paracetamol 500mg", "Analgesicos", "2.50", 40, False,
        [("A-001", 50, 300), ("B-002", 30, 20)],
    ),
    ("Ibuprofeno 400mg", "Analgesicos", "3.80", 30, False, [("I-101", 100, 200)]),
    ("Amoxicilina 500mg", "Antibioticos", "9.90", 25, True, [("AM-77", 10, 120)]),  # stock bajo
    ("Jabon antibacterial", "Higiene", "4.20", 15, False, [("J-12", 40, 400)]),
    ("Vitamina C 1g", "Suplementos", "7.50", 20, False, [("V-5", 60, 15)]),  # por vencer
]


def run() -> None:
    with SessionLocal() as db:
        categorias: dict[str, Categoria] = {}
        for nombre in CATEGORIAS:
            cat = db.scalar(select(Categoria).where(Categoria.nombre == nombre))
            if not cat:
                cat = Categoria(nombre=nombre)
                db.add(cat)
                db.flush()
            categorias[nombre] = cat

        for nombre, cat, precio, minimo, receta, lotes in PRODUCTOS:
            if db.scalar(select(Producto).where(Producto.nombre == nombre)):
                continue
            producto = Producto(
                nombre=nombre,
                precio=Decimal(precio),
                stock_minimo=minimo,
                requiere_receta=receta,
                categoria_id=categorias[cat].id,
            )
            producto.lotes = [
                Lote(
                    numero_lote=num,
                    cantidad=cant,
                    fecha_vencimiento=date.today() + timedelta(days=dias),
                )
                for num, cant, dias in lotes
            ]
            db.add(producto)
        db.commit()
    print("Semilla aplicada.")


if __name__ == "__main__":
    run()
