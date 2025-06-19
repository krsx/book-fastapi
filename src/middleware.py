import re
from fastapi import FastAPI, status
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import time
import logging


logger = logging.getLogger("uvicorn.access")
logger.disabled = True  # Disable default logging to avoid duplicate logs


def register_middleware(app: FastAPI):
    @app.middleware("http")
    async def custom_logging(request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        duration = time.time() - start_time
        message = f"{request.client.host}:{request.client.port} - {request.method} {request.url.path} - {response.status_code} in {duration}s"  # type: ignore
        print(message)  # Print to console
        return response

    @app.middleware("http")
    async def authorization_middleware(request: Request, call_next):
        public_path_patterns = [
            re.compile(r"^/api/v\d+/auth/signup/?$"),
            re.compile(r"^/api/v\d+/auth/login/?$"),
            re.compile(r"^/api/v\d+/auth/status/?$"),
            re.compile(r"^/api/v\d+/auth/refresh_token/?$"),
            re.compile(r"^/api/v\d+/auth/send_email/?$"),
            re.compile(r"^/api/v\d+/auth/password_reset/?$"),
            re.compile(r"^/api/v\d+/auth/verify_email/[^/]+/?$"),
            re.compile(r"^/api/v\d+/auth/password_reset_confirm/[^/]+/?$"),
            re.compile(r"^/docs/?.*"),
            re.compile(r"^/openapi\.json/?$"),
            re.compile(r"^/redoc/?.*"),
        ]

        path = request.url.path
        if any(pattern.match(path) for pattern in public_path_patterns):
            return await call_next(request)
        elif "Authorization" not in request.headers:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={
                    "message": "Authorization header is missing",
                    "error_code": "missing_authorization_header",
                },
            )

        return await call_next(request)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
        allow_credentials=True,
    )

    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["*"],
    )
