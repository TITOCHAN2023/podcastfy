from fastapi import FastAPI

from logger import logger

from routes.router import root_router




def create_app() -> FastAPI:
    app = FastAPI(
        title="CaizzzAI API",
        version="0.0.1",
    )

    # add routers
    app.include_router(root_router)
    logger.info("Init app successfully")
    return app
