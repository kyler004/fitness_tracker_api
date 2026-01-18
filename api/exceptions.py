from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Custom exception handler to provide more user-friendly error messages
    """
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)
    
    # Log the error
    logger.error(f'Error: {exc}, Context: {context}')
    
    if response is not None:
        # Customize the response format
        custom_response_data = {
            'error': True,
            'status_code': response.status_code,
            'message': 'An error occurred',
            'details': response.data
        }
        
        # Add more context for specific errors
        if response.status_code == 404:
            custom_response_data['message'] = 'Resource not found'
        elif response.status_code == 403:
            custom_response_data['message'] = 'Permission denied'
        elif response.status_code == 401:
            custom_response_data['message'] = 'Authentication required'
        elif response.status_code == 400:
            custom_response_data['message'] = 'Invalid request data'
        elif response.status_code >= 500:
            custom_response_data['message'] = 'Server error occurred'
        
        response.data = custom_response_data
    
    return response
