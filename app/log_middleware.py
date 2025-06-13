from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, StreamingResponse
from typing import Callable
import uuid
import time
import logging
import traceback

logger = logging.getLogger("SENTIBOT")

class LoggingAndTimingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.perf_counter()
        request_id = str(uuid.uuid4())
        method = request.method
        path = request.url.path
        host = request.client.host

        # Skip logging for GET requests
        if method == "GET":
            return await call_next(request)

        # Read request body for non-GET requests
        try:
            request_body = await request.body()
        except Exception:
            request_body = b""

        try:
            response = await call_next(request)

            # Capture response body
            response_body = b""
            async for chunk in response.body_iterator:
                response_body += chunk

            # Recreate the response for further middleware or final response
            response = StreamingResponse(
                iter([response_body]),
                status_code=response.status_code,
                headers=dict(response.headers)
            )
            status_code = int(response.status_code)  # Ensure status_code is an integer

        except Exception as exc:
            end_time = time.perf_counter()
            duration = (end_time - start_time) * 1000  # Convert to milliseconds
            logger.error("Exception occurred", exc_info=True, extra={
                'request_id': request_id,
                'host': host,
                'path': path,
                'method': method,
                'status_code': 500,
                'response_time': duration,
                'error_code': str(exc),
                'stack_trace': traceback.format_exc()
            })
            raise exc

        end_time = time.perf_counter()
        duration = (end_time - start_time) * 1000  # Convert to milliseconds
        response.headers["X-Response-Time"] = f"{duration:.2f} ms"

        # Log combined request and response details for non-GET requests
        logger.info(
            "Request and Response Log",
            extra={
                'request_id': request_id,
                'host': host,
                'path': path,
                'method': method,
                'status_code': status_code,  # Status code should be an integer
                'response_time': duration,  # This should be a float
                'request_body': request_body.decode('utf-8', errors='ignore') if request_body else "",
                'response_body': response_body.decode('utf-8', errors='ignore') if response_body else ""
            }
        )

        return response
