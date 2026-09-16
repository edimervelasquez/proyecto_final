from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Reemplaza la URL por la cadena de conexión real de tu proyecto.
# Si usas MySQL (XAMPP/Workbench) sería algo así:
# SQLALCHEMY_DATABASE_URL = "mysql+pymysql://usuario:contraseña@localhost/creaciones_yuyita"
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:123456@localhost/yullita_creaciones_db" # Ejemplo temporal con SQLite

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    # connect_args={"check_same_thread": False} # Descomenta esta línea SOLO si usas SQLite
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()