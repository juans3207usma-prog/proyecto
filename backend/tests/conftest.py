import os
from datetime import date, timedelta

# Valores de prueba: deben existir antes de importar la app (config los exige).
os.environ.setdefault("DATABASE_URL", "sqlite://")
os.environ.setdefault("SECRET_KEY", "test")

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402
from sqlalchemy.pool import StaticPool  # noqa: E402

from app.compartido.database import Base, get_db  # noqa: E402
from app.main import app  # noqa: E402
from app.models import Categoria, Lote, Producto  # noqa: E402


@pytest.fixture
def db():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    with sessionmaker(bind=engine, expire_on_commit=False)() as session:
        yield session


@pytest.fixture
def producto(db):
    """Paracetamol con dos lotes: A vence en 300 dias, B en 20 (B sale primero)."""
    categoria = Categoria(nombre="Analgesicos")
    db.add(categoria)
    db.flush()
    p = Producto(nombre="Paracetamol", precio=2, stock_minimo=40, categoria_id=categoria.id)
    db.add(p)
    db.flush()
    db.add_all(
        [
            Lote(
                producto_id=p.id,
                numero_lote="A",
                cantidad=50,
                fecha_vencimiento=date.today() + timedelta(days=300),
            ),
            Lote(
                producto_id=p.id,
                numero_lote="B",
                cantidad=30,
                fecha_vencimiento=date.today() + timedelta(days=20),
            ),
        ]
    )
    db.commit()
    return p


@pytest.fixture
def client(db):
    app.dependency_overrides[get_db] = lambda: db
    yield TestClient(app)
    app.dependency_overrides.clear()
