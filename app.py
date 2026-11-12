from backend.config import Config
from backend.main import app

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "backend.main:app",
        host=Config.HOST,
        port=Config.PORT,
        reload=Config.APP_ENV == "development",
    )
