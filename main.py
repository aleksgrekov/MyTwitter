from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from uvicorn import run

from router import router

app = FastAPI()
app.include_router(router)

app.mount("/css", StaticFiles(directory="dist/css"), name="css")
app.mount("/js", StaticFiles(directory="dist/js"), name="js")
app.mount("/", StaticFiles(directory="dist"), name="static_root")

if __name__ == '__main__':
    run("main:app", port=8000, host='127.0.0.1', reload=True)
