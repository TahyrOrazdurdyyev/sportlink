"""
Custom middleware for MongoDB project
"""
import logging
from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse

logger = logging.getLogger(__name__)


class MongoDBMiddleware(MiddlewareMixin):
    """Middleware to handle MongoDB-specific operations"""
    
    def process_request(self, request):
        """Process incoming requests"""
        # Add request ID for tracking
        import uuid
        request.request_id = str(uuid.uuid4())[:8]
        
        # Log API requests
        if request.path.startswith('/api/'):
            logger.info(f"API Request [{request.request_id}]: {request.method} {request.path}")
        
        return None
    
    def process_response(self, request, response):
        """Process responses"""
        # Add request ID to response headers
        if hasattr(request, 'request_id'):
            response['X-Request-ID'] = request.request_id
        
        return response
    
    def process_exception(self, request, exception):
        """Handle exceptions"""
        if hasattr(request, 'request_id'):
            logger.error(f"Exception [{request.request_id}]: {str(exception)}")
        
        # Return JSON error for API endpoints
        if request.path.startswith('/api/'):
            return JsonResponse({
                'error': 'Internal server error',
                'request_id': getattr(request, 'request_id', 'unknown')
            }, status=500)
        
        return None


class CorsMiddleware(MiddlewareMixin):
    """Simple CORS middleware"""
    
    def process_response(self, request, response):
        """Add CORS headers"""
        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Methods'] = 'GET, POST, PUT, PATCH, DELETE, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        
        return response


