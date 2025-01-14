from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from uvicorn import run

from src.database.service import async_session, create_tables, delete_tables
from src.logger_setup import get_logger
from src.prepare_data import populate_database
from src.routers.home_router import home_route
from src.routers.media_router import media_router
from src.routers.tweet_router import tweet_router
from src.routers.user_router import user_router

main_logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(fast_api: FastAPI):
    await delete_tables()
    main_logger.info("База очищена")
    await create_tables()
    main_logger.info("База заполнена тестовыми данными")

    async with async_session() as session:
        await populate_database(session)

    main_logger.info("База готова к работе")
    yield
    main_logger.info("Выключение")


app = FastAPI(lifespan=lifespan)
app.include_router(user_router)
app.include_router(tweet_router)
app.include_router(media_router)
app.include_router(home_route)

app.mount("/css", StaticFiles(directory="../dist/css"), name="css")
app.mount("/js", StaticFiles(directory="../dist/js"), name="js")
app.mount("/", StaticFiles(directory="../dist"), name="static_root")

if __name__ == "__main__":
    run("main:app", host="127.0.0.1", reload=True)
