from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from uvicorn import run

from logger.logger_setup import get_logger
from src.database.service import create_tables, delete_tables

from src.routers.api_router import api_router
from src.routers.home_router import home_route

main_logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(fast_api: FastAPI):
    await delete_tables()
    main_logger.info("База очищена")
    await create_tables()
    main_logger.info("База заполнена тестовыми данными")

    main_logger.info("База готова к работе")
    yield
    main_logger.info("Выключение")


app = FastAPI(lifespan=lifespan)
app.include_router(api_router)
app.include_router(home_route)


app.mount("/css", StaticFiles(directory="../dist/css"), name="css")
app.mount("/js", StaticFiles(directory="../dist/js"), name="js")
app.mount("/", StaticFiles(directory="../dist"), name="static_root")

if __name__ == '__main__':
    run("main:app", port=8000, host='127.0.0.1', reload=True)
