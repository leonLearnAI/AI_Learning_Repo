
from fastapi import FastAPI
from src.app.routers.health import router as health_router
from src.app.routers.ask import router as ask_router

def create_app() -> FastAPI:

    app = FastAPI(title="Book Intelligence Assistant", version="0.1.0")
    app.include_router(health_router)
    app.include_router(ask_router)
    return app

app = create_app()
