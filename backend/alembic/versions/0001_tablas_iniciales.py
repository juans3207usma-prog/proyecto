"""tablas iniciales

Revision ID: 0001
Revises:
Create Date: 2026-11-23
"""
import sqlalchemy as sa

from alembic import op

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "categorias",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("nombre", sa.String(80), nullable=False, unique=True),
    )
    op.create_table(
        "productos",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("nombre", sa.String(120), nullable=False),
        sa.Column("precio", sa.Numeric(10, 2), nullable=False),
        sa.Column("stock_minimo", sa.Integer(), nullable=False),
        sa.Column("requiere_receta", sa.Boolean(), nullable=False),
        sa.Column("activo", sa.Boolean(), nullable=False),
        sa.Column("categoria_id", sa.Integer(), sa.ForeignKey("categorias.id"), nullable=False),
        sa.CheckConstraint("precio > 0", name="ck_producto_precio"),
        sa.CheckConstraint("stock_minimo >= 0", name="ck_producto_stock_minimo"),
    )
    op.create_table(
        "lotes",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("producto_id", sa.Integer(), sa.ForeignKey("productos.id"), nullable=False),
        sa.Column("numero_lote", sa.String(40), nullable=False),
        sa.Column("cantidad", sa.Integer(), nullable=False),
        sa.Column("fecha_vencimiento", sa.Date(), nullable=False),
        sa.CheckConstraint("cantidad >= 0", name="ck_lote_cantidad"),
    )
    op.create_index("ix_lotes_fecha_vencimiento", "lotes", ["fecha_vencimiento"])
    op.create_table(
        "movimientos",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("producto_id", sa.Integer(), sa.ForeignKey("productos.id"), nullable=False),
        sa.Column("tipo", sa.String(10), nullable=False),
        sa.Column("cantidad", sa.Integer(), nullable=False),
        sa.Column("motivo", sa.String(200), nullable=True),
        sa.Column("creado_en", sa.DateTime(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("movimientos")
    op.drop_index("ix_lotes_fecha_vencimiento", table_name="lotes")
    op.drop_table("lotes")
    op.drop_table("productos")
    op.drop_table("categorias")
