import logging
from starlette.requests import Request
from starlette.middleware.base import BaseHTTPMiddleware
import time


logging.basicConfig(
    level=logging.INFO,
    filename="logtext.log",
    format="%(asctime)s - %(name)s - %(levelname)s - %(messege)s"
)


def get_logger(name):
    global logger; 
    logger = logging.getLogger(name)
    return logger


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        #start time
        start_time = time.time()
        #log the incoming request
        logger.info(f"Start request : {request.method} {request.url}")
        #call the actual request handler
        response = await call_next(request)
        #log the response details
        process_time = time.time() - start_time
        logger.info(f"Finished request: {request.method} {request.url} - Status code : {response.status_code} - Duration : {process_time:.4f} seconds")
        return response
