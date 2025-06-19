from fastapi import FastAPI, status
from contextlib import asynccontextmanager

from fastapi.responses import JSONResponse

from src.books.routers import book_router
from src.auth.routers import auth_router
from src.reviews.routers import review_router
from src.db.main import init_db
from src.db.redis import close_redis_connection
from src.errors import register_error_handlers
from src.middleware import register_middleware
from src.config import Config


VERSION = Config.API_VERSION


# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     print("Server is starting up...")
#     await init_db()
#     yield
#     print("Server is shutting down...")
#     await close_redis_connection()


app = FastAPI(
    # lifespan=lifespan,
    title="Books",
    description="A simple RESTful API for books",
    version=VERSION,
)

app.include_router(
    book_router,
    prefix=f"/api/{VERSION}/books",
    tags=["books"],
)

app.include_router(
    auth_router,
    prefix=f"/api/{VERSION}/auth",
    tags=["auth"],
)

app.include_router(
    review_router,
    prefix=f"/api/{VERSION}/reviews",
    tags=["reviews"],
)


register_error_handlers(app)

register_middleware(app)
