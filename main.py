from fastapi import FastAPI

from src.handlers.handlers import exception_handler
from src.routers.media_router import media_router
from src.routers.tweet_router import tweet_router
from src.routers.user_router import user_router

app = FastAPI(title="Twitter Clone API", version="1.0.0")

app.add_exception_handler(Exception, exception_handler)

app.include_router(user_router)
app.include_router(tweet_router)
app.include_router(media_router)
