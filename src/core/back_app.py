from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from src.db.session import engine
from src.db.base import Base
from src.api.routes import user as user_routes
from src.api.routes import cleanup as jobs_routes
from src.api.routes import cards as card_routes
from src.api.routes import savings as savings_routes
from src.api.routes import bills as bills_routes
from src.core.config import settings

class BackendApp(FastAPI):
    def __init__(self):
        super().__init__()
        self.__initializeRoutes(super())
        super().add_middleware(
            CORSMiddleware,
            allow_origins=settings.ORIGINS,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        Base.metadata.create_all(bind=engine)
        super().mount("/static", StaticFiles(directory="src/static"), name="static")

    def __initializeRoutes(self, app: FastAPI) -> None:
        app.include_router(user_routes.router, prefix="/auth", tags=["auth"])
        app.include_router(jobs_routes.router, tags=["miscallenious"])
        app.include_router(card_routes.router, prefix="/card", tags=["card"])
        app.include_router(savings_routes.router, prefix="/savings", tags=["savings"])
        app.include_router(bills_routes.router, prefix="/bills", tags=["bills"])

        @self.get("/")
        def read_root():
            return {"Status": "Server up and running"}