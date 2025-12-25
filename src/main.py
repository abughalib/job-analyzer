import os
import uvicorn
from dotenv import load_dotenv
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
import logging

from utils.vars import get_app_path
from utils.constants import UPLOADED_FILE_FOLDER
from utils.app_config import AppConfig
from routes.app_route import router
from job_analyzer.database.models import Base
from job_analyzer.database.layoff_db import (
    layoff_db_context,
    layoff_db_session,
    layoff_db_engine,
)

load_dotenv()

# Load app config
config = AppConfig.load_default()

from utils.logging_utils import setup_logging

setup_logging(config.app_setting.logging)


@asynccontextmanager
async def lifespan(app: FastAPI):

    logging.info("Application startup: Initializing Database...")

    # Create uploads directory if it doesn't exist
    uploads_path = get_app_path().joinpath(UPLOADED_FILE_FOLDER)
    if not uploads_path.exists():
        os.makedirs(uploads_path)
        logging.info(f"Created uploads directory at: {uploads_path}")

    async with layoff_db_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    logging.info("Database initialization complete.")

    yield

    logging.info("Application shutdown: Disposing database engine...")

    await layoff_db_engine.dispose()

    logging.info("Engine Disposed")


app = FastAPI(lifespan=lifespan)


@app.middleware("http")
async def db_session_middleware(request: Request, call_next):
    """
    Creates a new DB session for each request, sets it in the context
    and ensures it's closed after the request is finished
    """

    try:
        session = layoff_db_session()

        token = layoff_db_context.set(session)

        response = await call_next(request)

    finally:
        await session.close()  # type: ignore
        layoff_db_context.reset(token)  # type: ignore

    return response


app.include_router(router, prefix="/api/v1")

if __name__ == "__main__":

    logging.info("Local inference initialized.")

    uvicorn.run(app, host="0.0.0.0", port=8100)
