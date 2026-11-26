"""Patron Unit of Work: un grupo de cambios se guarda completo o no se guarda."""

from collections.abc import Iterator
from contextlib import contextmanager

from sqlalchemy.orm import Session


@contextmanager
def transaccion(db: Session) -> Iterator[Session]:
    """Confirma al salir del bloque; ante cualquier error revierte y lo relanza.

    La `Session` de SQLAlchemy ya lleva la cuenta de los cambios; esto fija en un
    solo lugar cuando se confirman. No anidar: el bloque interior confirmaria antes
    de que termine el exterior.
    """
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
