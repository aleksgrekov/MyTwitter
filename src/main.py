from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from uvicorn import run

from src.database.service import async_session
from src.handlers.handlers import exception_handler
from src.prepare_data import populate_database
from src.routers.home_router import home_route
from src.routers.media_router import media_router
from src.routers.tweet_router import tweet_router
from src.routers.user_router import user_router


@asynccontextmanager
async def lifespan(fast_api: FastAPI):
    async with async_session() as session:
        await populate_database(session)
    print("База заполнена тестовыми данными")

    print("База готова к работе")
    yield
    print("Выключение")


app = FastAPI(lifespan=lifespan, title="Twitter Clone API", version="1.0.0")

app.add_exception_handler(Exception, exception_handler)

app.include_router(user_router)
app.include_router(tweet_router)
app.include_router(media_router)
app.include_router(home_route)

path_to_dist = Path(__file__).resolve().parent.parent / "dist"

app.mount("/css", StaticFiles(directory=path_to_dist / "css"), name="css")
app.mount("/js", StaticFiles(directory=path_to_dist / "js"), name="js")
app.mount("/", StaticFiles(directory=path_to_dist), name="static_root")

if __name__ == "__main__":
    run("main:app", host="0.0.0.0")
