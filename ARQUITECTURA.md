# Arquitectura y convenciones de desarrollo

## Estructura

El sistema es una aplicación web cliente-servidor con un backend monolítico
organizado por capas:

```text
Navegador
  └── React: páginas, componentes y servicios HTTP
        └── API REST: rutas FastAPI y esquemas Pydantic
              └── Controllers: coordinan entrada HTTP y selección del caso de uso
                    └── Services: reglas de negocio y transacciones
                          └── Repositories: consultas y persistencia SQLAlchemy
                                └── MySQL
```

Cada dominio del backend tiene su controller bajo `backend/controllers`.
FastAPI valida la solicitud con Pydantic y las rutas entregan el resultado al
controller; este coordina el servicio de dominio correspondiente. Los
servicios concentran reglas de negocio y transacciones, mientras que los
repositorios concentran las consultas SQL. En el frontend, las páginas
coordinan estado y formularios, los componentes reutilizables presentan la
interfaz y `src/services` centraliza las llamadas HTTP.

Las pantallas de producción e inventario separan el estado, la carga de datos
y las acciones de formulario en hooks de `frontend/src/hooks`; las páginas
conservan la composición visual y sus componentes y clases CSS existentes. La
lógica de registro y consulta de trazos de producción vive en
`backend/services/trazo_service.py`; las rutas conservan sus mismos endpoints.

## Reglas para cambios nuevos

- Validar la forma de las solicitudes con esquemas Pydantic.
- Mantener rutas enfocadas en HTTP y delegar la coordinación al controller.
- Mantener los controllers enfocados en traducir/coordinar la petición; las
  reglas de negocio permanecen en services.
- Mantener permisos y obtención del usuario autenticado en los límites HTTP;
  validar también las reglas del dominio en el servicio cuando sea necesario.
- Mantener consultas SQL en repositorios. No cargar colecciones grandes para
  calcular totales que la base pueda agregar.
- Mantener juntas las operaciones que deban confirmarse o revertirse como una
  sola transacción. Los repositorios no deben confirmar transacciones.
- Evitar lógica de negocio en rutas, componentes visuales o configuración de
  arranque.
- Antes de retirar modelos heredados, comprobar sus referencias y datos en la
  base real; algunos se conservan por compatibilidad.

## Inicio y esquema

Importar `backend.main` ya no se conecta a la base ni crea tablas. La aplicación
ejecuta `initialize_database()` durante su ciclo de vida de inicio. Esa rutina
mantiene la creación compatible existente, semillas idempotentes de roles y
áreas, y el backfill de productos que ya tenían ficha técnica.

La rutina actual **no reemplaza un sistema formal de migraciones versionadas**.
Los cambios futuros de esquema deben planificarse con migraciones revisables y
probadas sobre una copia antes de aplicarse a producción.

## Movimientos auditables y alertas de insumos

Cada nueva recepción y cada consumo al crear una orden registra un movimiento
en `movimiento_insumo` dentro de la misma transacción que actualiza el saldo.
Las entradas se guardan positivas y los consumos de producción negativos; el
movimiento conserva usuario, fecha, costo y referencia al ingreso u orden.
Los registros históricos no se reconstruyen porque no hay una fuente fiable
para atribuir quién hizo cada consumo anterior.

El nivel mínimo se configura por insumo; los insumos existentes reciben mínimo
`0` durante la actualización compatible del esquema, por lo que el stock cero
también genera alerta con ese valor inicial. La pantalla de insumos permite
consultar alertas e historial, y solo el administrador puede cambiar mínimos.
El resumen del dashboard incluye el número y detalle de insumos en o por debajo
de su nivel mínimo.

## Pruebas y comprobaciones

Las pruebas de regresión usan SQLite en memoria; no requieren conectarse a la
base MySQL de la empresa. Para las pruebas HTTP instala el cliente de pruebas
de Starlette:

```powershell
$env:DATABASE_URL = "sqlite://"
.\venv\Scripts\python.exe -m pip install -r requirements-test.txt
.\venv\Scripts\python.exe -m unittest discover -s tests -v
.\venv\Scripts\python.exe -m compileall -q backend tests
```

`backend.main.create_app(engine_prueba)` permite crear una instancia FastAPI
aislada con un engine de pruebas. Sus endpoints usan sesiones conectadas a ese
engine y el ciclo de vida inicializa el esquema de prueba. No se debe ejecutar
una prueba HTTP usando el engine real de producción.

Las pruebas HTTP con `TestClient` verifican autenticación, CORS, permisos por
rol, validación Pydantic (HTTP 422) y el contrato JSON de los endpoints.
Las pruebas de servicios cubren el resumen financiero, el arranque
idempotente y el flujo integrado de orden, etapas, retrasos, calidad,
existencias, traslados y venta.

Para el frontend:

```powershell
cd frontend
npm run lint
npm run build
```

Añade un test de regresión al modificar cualquiera de esas reglas.
