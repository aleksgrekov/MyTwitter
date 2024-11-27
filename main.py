from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from uvicorn import run

from router import router
from database import create_tables, delete_tables, populate_database, create_session


@asynccontextmanager
async def lifespan(fast_api: FastAPI):
    await delete_tables()
    print("База очищена")
    await create_tables()

    async with create_session() as session:
        await populate_database(session)
        print("База заполнена тестовыми данными")

    print("База готова к работе")
    yield
    print("Выключение")


app = FastAPI(lifespan=lifespan)
app.include_router(router)

app.mount("/css", StaticFiles(directory="dist/css"), name="css")
app.mount("/js", StaticFiles(directory="dist/js"), name="js")
app.mount("/", StaticFiles(directory="dist"), name="static_root")

if __name__ == '__main__':
    run("main:app", port=8000, host='127.0.0.1', reload=True)
