from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
import time
from app.utils.logger import logger

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Proceed with request
        response = await call_next(request)
        
        # Timing
        process_time = time.time() - start_time
        
        # Info to log
        ip = request.client.host if request.client else "unknown"
        method = request.method
        url = str(request.url)
        
        # Log basic request info
        logger.info(f"{method} {url} from {ip} completed in {process_time:.4f}s")
        
        return response
