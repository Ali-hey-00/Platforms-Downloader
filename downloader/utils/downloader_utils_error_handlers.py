import logging
import traceback
from typing import Dict, Any, Optional
from datetime import datetime
from django.http import JsonResponse
from rest_framework import status
from rest_framework.views import exception_handler
from django.core.exceptions import ValidationError
from requests.exceptions import RequestException
from ..exceptions import (
    DownloadError,
    MediaNotFoundError,
    RateLimitExceeded,
    InvalidURLError
)

logger = logging.getLogger(__name__)

class ErrorResponse:
    """Standardized error response builder"""
    
    @staticmethod
    def create(
        error_code: str,
        message: str,
        status_code: int,
        details: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None
    ) -> JsonResponse:
        """
        Create a standardized error response
        
        Args:
            error_code: Unique error identifier
            message: Human-readable error message
            status_code: HTTP status code
            details: Additional error details
            request_id: Unique request identifier for tracking
        """
        response_data = {
            'error': {
                'code': error_code,
                'message': message,
                'timestamp': datetime.utcnow().isoformat(),
                'request_id': request_id
            }
        }
        
        if details:
            response_data['error']['details'] = details
            
        return JsonResponse(response_data, status=status_code)

def custom_exception_handler(exc: Exception, context: Dict) -> JsonResponse:
    """
    Custom exception handler for REST framework views
    
    Args:
        exc: The raised exception
        context: Additional context about the error
    """
    # Generate unique request ID for tracking
    request_id = context['request'].META.get('X-Request-ID')
    
    # Log the exception with stack trace
    logger.error(
        f"Exception occurred: {str(exc)}",
        extra={
            'request_id': request_id,
            'stack_trace': traceback.format_exc(),
            'user': getattr(context['request'].user, 'username', 'anonymous')
        }
    )
    
    # Handle custom exceptions
    if isinstance(exc, DownloadError):
        return ErrorResponse.create(
            'DOWNLOAD_ERROR',
            str(exc),
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={'url': getattr(exc, 'url', None)},
            request_id=request_id
        )
    
    elif isinstance(exc, MediaNotFoundError):
        return ErrorResponse.create(
            'MEDIA_NOT_FOUND',
            str(exc),
            status.HTTP_404_NOT_FOUND,
            request_id=request_id
        )
    
    elif isinstance(exc, RateLimitExceeded):
        return ErrorResponse.create(
            'RATE_LIMIT_EXCEEDED',
            str(exc),
            status.HTTP_429_TOO_MANY_REQUESTS,
            details={'retry_after': exc.retry_after},
            request_id=request_id
        )
    
    elif isinstance(exc, InvalidURLError):
        return ErrorResponse.create(
            'INVALID_URL',
            str(exc),
            status.HTTP_400_BAD_REQUEST,
            request_id=request_id
        )
    
    elif isinstance(exc, ValidationError):
        return ErrorResponse.create(
            'VALIDATION_ERROR',
            'Invalid input data',
            status.HTTP_400_BAD_REQUEST,
            details={'errors': exc.message_dict},
            request_id=request_id
        )
    
    elif isinstance(exc, RequestException):
        return ErrorResponse.create(
            'NETWORK_ERROR',
            'Network error occurred',
            status.HTTP_503_SERVICE_UNAVAILABLE,
            details={'original_error': str(exc)},
            request_id=request_id
        )
    
    # Handle any other unexpected exceptions
    response = exception_handler(exc, context)
    if response is None:
        return ErrorResponse.create(
            'INTERNAL_SERVER_ERROR',
            'An unexpected error occurred',
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            request_id=request_id
        )
    
    return response