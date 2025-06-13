import os

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

load_dotenv()

from app.config.routes import router  
from app.exception_handlers import validation_exception_handler, ApiException, api_exception_handler
from app.log_middleware import LoggingAndTimingMiddleware


app = FastAPI()

app.add_middleware(LoggingAndTimingMiddleware)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(ApiException, handler=api_exception_handler)
app.include_router(router)
app.mount("/static", StaticFiles(directory=os.path.join("app", "static")), name="static")

allowed_origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "OPTIONS"],
    allow_headers=["*"],
)


user_host = os.getenv("HOST_NAME", "127.0.0.1")
user_port = int(os.getenv("PORT", "9000"))


if __name__ == "__main__":
    uvicorn.run(app, host=user_host, port=user_port)