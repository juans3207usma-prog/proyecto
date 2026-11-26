# Arquitectura

**Monolito modular + capas dentro de cada modulo.** Los modulos separan por tema del
negocio; las capas separan por responsabilidad.

## Estructura

```
proyecto/
├── backend/
│   ├── app/
│   │   ├── main.py            # arma la app y registra routers
│   │   ├── models.py          # registro de modelos (Alembic, semilla, pruebas)
│   │   ├── compartido/        # config, base de datos, errores
│   │   └── modulos/
│   │       ├── catalogo/      # categorias y productos
│   │       │   ├── api/       # rutas HTTP y esquemas
│   │       │   ├── servicios/ # casos de uso y transacciones
│   │       │   └── datos/     # modelos y consultas
│   │       ├── inventario/    # lotes y movimientos
│   │       │   ├── api/
│   │       │   ├── servicios/
│   │       │   ├── datos/
│   │       │   └── dominio/   # regla FEFO, Python puro
│   │       └── alertas/       # stock bajo y proximos a vencer
│   │           ├── api/
│   │           ├── servicios/
│   │           └── datos/
│   ├── alembic/               # migraciones
│   ├── tests/
│   │   ├── unitarias/         # FEFO y reglas de arquitectura (sin BD)
│   │   ├── servicios/         # casos de uso con BD en memoria
│   │   └── integracion/       # API HTTP de punta a punta
│   └── seed.py
├── frontend/src/
│   ├── api/                   # llamadas HTTP, un archivo por modulo
│   ├── componentes/           # pintan la pantalla y manejan formularios
│   ├── estilos/
│   └── main.js                # conecta api y componentes
└── docs/
```

## Capas de un modulo

```
api  ->  servicios  ->  datos
              │
              └──>  dominio
```

| Capa | Que hace | Que no debe hacer |
|---|---|---|
| `api` | Recibe la peticion, valida, llama al servicio | Consultar la base de datos |
| `servicios` | Coordina el caso de uso y delimita la transaccion | Conocer HTTP o esquemas |
| `datos` | Define modelos y consultas | Confirmar transacciones ni decidir reglas |
| `dominio` | Reglas puras del negocio | Importar FastAPI, SQLAlchemy o Pydantic |

## Patron Unit of Work

Toda escritura pasa por `compartido/transaccion.py`:

```python
with transaccion(db):
    ...  # todos los cambios del caso de uso
```

Al salir del bloque se confirma; si algo falla se revierte todo y el error se relanza.
Los modulos no llaman `commit` ni `rollback` directamente (una prueba lo comprueba) y los
bloques no se anidan.

## Dependencias entre modulos

```
alertas  ->  inventario  ->  catalogo
```

- Excepcion unica: `catalogo/api/productos.py` lee `inventario/servicios/stock.py`
  para mostrar el stock junto a cada producto.
- `inventario` usa `catalogo/servicios/productos.obtener` para validar productos.
- `inventario/datos` y `alertas/datos` usan los modelos de los modulos de los que
  dependen, para poder relacionar y cruzar tablas.

Estas reglas se comprueban en `backend/tests/unitarias/test_arquitectura.py`.

## Como agregar un modulo (ejemplo: proveedores)

1. Crear `app/modulos/proveedores/` con `api/`, `servicios/` y `datos/` (cada una con
   su `__init__.py`).
2. Definir los modelos en `datos/modelos.py` e importarlos en `app/models.py`.
3. Generar la migracion: `alembic revision --autogenerate -m "proveedores"`.
4. Escribir consultas en `datos/repositorio.py` y casos de uso en `servicios/`.
5. Exponer las rutas en `api/` y sumar el router a `ROUTERS` en `app/main.py`.
6. Agregar pruebas y, si depende de otro modulo, su regla en `test_arquitectura.py`.

## Por que no hexagonal completa ni microservicios

Con cuatro tablas, interfaces para cada repositorio o servicios separados agregarian
trabajo sin beneficio. La estructura actual permite dar ese paso despues: los
repositorios ya concentran las consultas y los modulos tienen limites claros.

## Mejoras futuras

- Autenticacion como modulo nuevo (`modulos/usuarios`).
- Paginacion en los listados cuando crezca el volumen de datos.
- Pruebas de concurrencia contra PostgreSQL.
