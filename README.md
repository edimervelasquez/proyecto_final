SIES Yullita — Sistema Integral de Gestión Textil

Plataforma web para la gestión operativa, inventario, producción, control de calidad, mermas y ventas del taller textil Yullita Creaciones.

🛠️ Stack Tecnológico

Backend: Python 3, FastAPI, SQLAlchemy, Pydantic.

Base de Datos: MySQL (28 tablas relacionales).

Frontend: React / Vite, CSS moderno (Industrial Dark Theme).

🚀 Instalación y Ejecución Rápida

1. Configuración

Desde la raíz del proyecto, crea `.env` desde la plantilla y configura la
conexión a la base de datos y el correo SMTP:

```powershell
Copy-Item .env.example .env
```

Edita `DATABASE_URL` y, para recuperación por correo, las variables `SMTP_*`.
El `.env` de la raíz es compartido por backend y frontend, está excluido de
Git y no debe publicarse. El backend genera las claves de seguridad al iniciar.

2. Backend (API)

Desde la raíz del proyecto:

python -m venv venv
# En Windows:
venv\Scripts\Activate.ps1
# En Linux/Mac:
source venv/bin/activate

pip install -r requirements.txt
python app.py


El servidor levantará por defecto en http://127.0.0.1:8000. La base de datos
debe existir y estar disponible según `DATABASE_URL`.

3. Frontend (Interfaz Web)

cd frontend
npm install
npm run dev


La aplicación abrirá en http://localhost:5173. Su URL de API se configura con
`VITE_API_URL` en el `.env` de la raíz.

👥 Roles del Sistema

Administrador: Control total (dashboard financiero, aprobación de empleados, insumos, fichas técnicas, producción, calidad, mermas y ventas).

Trabajador: Gestión operativa de órdenes de producción, registro de mermas y control de calidad.

Vendedor: Consulta de inventario de prendas y registro de ventas al detal y mayoristas.
