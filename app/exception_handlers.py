from typing import Any
from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Custom exception handler for request validation errors.
    """
    # Extract validation errors into a readable format

    error_messages = []
    for err in exc.errors():
        # Construct field path, excluding the first element ('body')
        field_path = '.'.join(str(loc) for loc in err['loc'][1:])
        message = err['msg']
        error_messages.append(f"{field_path}: {message}")
    full_message = "; ".join(error_messages)
    return JSONResponse(
        status_code=422,
        content={
            "status": False,
            "message": f"Validation Error: {full_message}",
            "data": None
        }
    )


class ApiException(Exception):
    def __init__(self, status_code:int=400, status:bool=False, message:str="Api Exception", data:Any=None):
        self.status_code = status_code
        self.status = status
        self.message = message
        self.data = data


async def api_exception_handler(request: Request, exc: ApiException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": exc.status,
            "message":exc.message,
            "data":exc.data
        },
    )
