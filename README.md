# Inventario Farmacia

Gestion de inventario para farmacia: productos, categorias, movimientos con lotes y
**FEFO** (primero en vencer, primero en salir), y alertas de stock bajo y de vencimiento.

**Stack:** FastAPI + SQLAlchemy + Alembic + PostgreSQL | Vite (JS) | pytest, ruff, ESLint.

## Requisitos

- Python 3.11 o superior
- Node 20 o superior
- Docker (para PostgreSQL)

## Puesta en marcha desde cero

Todos los comandos son para PowerShell, desde la raiz del repositorio.

### 1. Variables de entorno

```powershell
Copy-Item .env.example .env
```

Edita `SECRET_KEY` en `.env` con un valor propio. No subas `.env` al repositorio.

### 2. Base de datos

```powershell
docker compose up -d
```

### 3. Backend

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
alembic upgrade head
python seed.py
uvicorn app.main:app --reload
```

- API: http://localhost:8000 (documentacion interactiva en `/docs`).
- `seed.py` es idempotente: puedes ejecutarlo varias veces sin duplicar datos.

### 4. Frontend (en otra terminal)

```powershell
cd frontend
Copy-Item .env.example .env
npm install
npm run dev
```

UI: http://localhost:5173

## Pruebas y calidad

```powershell
cd backend
pytest --cov --cov-fail-under=70   # cobertura de servicios y FEFO; falla bajo 70 %
ruff check .

cd ..\frontend
npx eslint .
```

Las pruebas usan SQLite en memoria (rapidas, sin Docker). El bloqueo de filas
(`with_for_update`) solo tiene efecto en PostgreSQL; SQLite lo ignora.

## Arquitectura: monolito modular

```
backend/app/
├── catalogo/     # categorias y productos (modelos, schemas, servicios, routers)
├── inventario/   # lotes, movimientos, stock y la regla FEFO (fefo.py, funcion pura)
├── alertas/      # consultas de stock bajo y de proximos a vencer
├── compartido/   # config, base de datos, errores de negocio
└── main.py       # arma la app y registra los routers
```

Reglas de dependencia:

- `catalogo` (modelos y servicios) no conoce a `inventario`; `inventario` depende de `catalogo`.
- `alertas` solo lee de `catalogo` e `inventario`.
- Unica excepcion de lectura: el router de productos consulta `inventario.stock` para
  mostrar el stock junto a cada producto (una consulta, sin N+1).
- `inventario/fefo.py` no usa base de datos: decide de que lote y cuanto descontar. El
  servicio solo bloquea filas, aplica el plan y registra el movimiento.

## Decisiones tecnicas

| Decision | Motivo |
|---|---|
| Stock por **lote**, no por producto | Hace posible FEFO y el control de vencimientos. |
| Salida en **una sola transaccion** con `with_for_update()` | Todo o nada; evita ventas simultaneas sobre el mismo stock. |
| Modulos por dominio | Cada modulo agrupa lo suyo; las dependencias van en un solo sentido. |
| FEFO como funcion pura | Se prueba sin base de datos; el servicio solo la aplica. |
| Logica en servicios (`*service*.py`) | Separada de HTTP y facil de probar; la cobertura se mide ahi. |
| `Numeric`/`Decimal` para precios | Evita errores de redondeo de `float`. |
| Borrado logico de productos | Conserva la integridad del historial de movimientos. |
| Movimientos inmutables | Solo se insertan; las correcciones son movimientos de ajuste. |
| `CHECK (cantidad >= 0)` en lotes | La BD rechaza stock negativo aunque falle el codigo. |
| Alertas calculadas al consultar | Nunca quedan desactualizadas; no hay tabla extra. |

## Endpoints principales

| Metodo | Ruta | Descripcion |
|---|---|---|
| GET/POST | `/categorias` | Listar / crear |
| PUT/DELETE | `/categorias/{id}` | Actualizar / borrar (409 si tiene productos) |
| GET/POST | `/productos` | Listar (con stock) / crear |
| GET/PUT/DELETE | `/productos/{id}` | Detalle / actualizar / desactivar |
| POST | `/movimientos/entrada` | Crea un lote y registra la entrada |
| POST | `/movimientos/salida` | Descuenta con FEFO (409 si no hay stock) |
| GET | `/alertas/stock-bajo` | Productos bajo su minimo |
| GET | `/alertas/por-vencer?dias=30` | Lotes proximos a vencer |

## Flujo de trabajo en Git

`main` es estable y solo recibe cambios por Pull Request. Una rama por funcionalidad
(`feat/...`, `test/...`) y commits como `feat:`, `fix:`, `test:`. El CI ejecuta ruff,
pytest con cobertura, ESLint y el build del frontend.

## Pendiente (deseable)

Autenticacion con roles y dashboard con graficos.
