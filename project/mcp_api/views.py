"""
API views for MCP (Model Context Protocol) endpoints.
This module provides views for Python code execution and directory operations.
"""

import json
import logging
from typing import Dict, Any
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings
from .utils import execute_python_code, list_directory, list_directory_recursively

logger = logging.getLogger(settings.MCP_LOGGER)


@csrf_exempt
@require_http_methods(["POST"])
def run_python_code_view(request) -> JsonResponse:
    """
    Execute Python code in a user's directory.
    
    Expected payload:
    {
        "user_dir": "user_directory_name",
        "python_code": "print('Hello, World!')"
    }
    
    Args:
        request: The HTTP request object
        
    Returns:
        JsonResponse: Execution results in JSON format
    """
    # Debug logging
    if settings.DEBUG:
        logger.debug(f"MCP API: run_python_code request received from {request.META.get('REMOTE_ADDR', 'unknown')}")
    
    try:
        # Parse JSON payload
        data = json.loads(request.body)
        
        # Debug logging
        if settings.DEBUG:
            logger.debug(f"MCP API: run_python_code payload keys: {list(data.keys())}")
        
        # Validate required fields
        if 'user_dir' not in data:
            logger.error("MCP API: run_python_code missing 'user_dir' field")
            return JsonResponse({
                'success': False,
                'error': 'Missing required field: user_dir'
            }, status=400)
        
        if 'python_code' not in data:
            logger.error("MCP API: run_python_code missing 'python_code' field")
            return JsonResponse({
                'success': False,
                'error': 'Missing required field: python_code'
            }, status=400)
        
        user_dir = data['user_dir']
        python_code = data['python_code']
        
        # Validate data types
        if not isinstance(user_dir, str):
            logger.error("MCP API: run_python_code 'user_dir' must be a string")
            return JsonResponse({
                'success': False,
                'error': 'user_dir must be a string'
            }, status=400)
        
        if not isinstance(python_code, str):
            logger.error("MCP API: run_python_code 'python_code' must be a string")
            return JsonResponse({
                'success': False,
                'error': 'python_code must be a string'
            }, status=400)
        
        # Log the request
        logger.info(f"MCP API: Executing Python code for user_dir: {user_dir}")
        
        # Execute the Python code
        result = execute_python_code(user_dir, python_code)
        
        # Return the result
        return JsonResponse(result)
        
    except json.JSONDecodeError as e:
        logger.error(f"MCP API: run_python_code JSON decode error: {e}")
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON payload'
        }, status=400)
    except Exception as e:
        logger.error(f"MCP API: run_python_code unexpected error: {e}")
        return JsonResponse({
            'success': False,
            'error': f'Unexpected error: {str(e)}'
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def list_dir_view(request) -> JsonResponse:
    # return JsonResponse(data= {"asd" : "asd"}, status=200)
    """
    List contents of a directory for a specific user.
    
    Expected payload:
    {
        "user_dir": "user_directory_name",
        "dir_name": "optional_subdirectory"
    }
    
    Args:
        request: The HTTP request object
        
    Returns:
        JsonResponse: Directory listing in JSON format
    """
    # Debug logging
    if settings.DEBUG:
        logger.debug(f"MCP API: list_dir request received from {request.META.get('REMOTE_ADDR', 'unknown')}")
    
    try:
        # Parse JSON payload
        data = json.loads(request.body)
        
        # Debug logging
        if settings.DEBUG:
            logger.debug(f"MCP API: list_dir payload keys: {list(data.keys())}")
        
        # Validate required fields
        if 'user_dir' not in data:
            logger.error("MCP API: list_dir missing 'user_dir' field")
            return JsonResponse({
                'success': False,
                'error': 'Missing required field: user_dir'
            }, status=400)
        
        user_dir = data['user_dir']
        dir_name = data.get('dir_name', '')  # Optional field
        
        # Validate data types
        if not isinstance(user_dir, str):
            logger.error("MCP API: list_dir 'user_dir' must be a string")
            return JsonResponse({
                'success': False,
                'error': 'user_dir must be a string'
            }, status=400)
        
        if not isinstance(dir_name, str):
            logger.error("MCP API: list_dir 'dir_name' must be a string")
            return JsonResponse({
                'success': False,
                'error': 'dir_name must be a string'
            }, status=400)
        
        # Log the request
        logger.info(f"MCP API: Listing directory for user_dir: {user_dir}, dir_name: {dir_name}")
        
        # List the directory
        result = list_directory(user_dir, dir_name)
        
        # Return the result
        return JsonResponse(result)
        
    except json.JSONDecodeError as e:
        logger.error(f"MCP API: list_dir JSON decode error: {e}")
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON payload'
        }, status=400)
    except Exception as e:
        logger.error(f"MCP API: list_dir unexpected error: {e}")
        return JsonResponse({
            'success': False,
            'error': f'Unexpected error: {str(e)}'
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def list_dir_recursively_view(request) -> JsonResponse:
    """
    List contents of a directory recursively for a specific user.
    
    Expected payload:
    {
        "user_dir": "user_directory_name",
        "dir_name": "optional_subdirectory"
    }
    
    Args:
        request: The HTTP request object
        
    Returns:
        JsonResponse: Recursive directory listing in JSON format
    """
    # Debug logging
    if settings.DEBUG:
        logger.debug(f"MCP API: list_dir_recursively request received from {request.META.get('REMOTE_ADDR', 'unknown')}")
    
    try:
        # Parse JSON payload
        data = json.loads(request.body)
        
        # Debug logging
        if settings.DEBUG:
            logger.debug(f"MCP API: list_dir_recursively payload keys: {list(data.keys())}")
        
        # Validate required fields
        if 'user_dir' not in data:
            logger.error("MCP API: list_dir_recursively missing 'user_dir' field")
            return JsonResponse({
                'success': False,
                'error': 'Missing required field: user_dir'
            }, status=400)
        
        user_dir = data['user_dir']
        dir_name = data.get('dir_name', '')  # Optional field
        
        # Validate data types
        if not isinstance(user_dir, str):
            logger.error("MCP API: list_dir_recursively 'user_dir' must be a string")
            return JsonResponse({
                'success': False,
                'error': 'user_dir must be a string'
            }, status=400)
        
        if not isinstance(dir_name, str):
            logger.error("MCP API: list_dir_recursively 'dir_name' must be a string")
            return JsonResponse({
                'success': False,
                'error': 'dir_name must be a string'
            }, status=400)
        
        # Log the request
        logger.info(f"MCP API: Listing directory recursively for user_dir: {user_dir}, dir_name: {dir_name}")
        
        # List the directory recursively
        result = list_directory_recursively(user_dir, dir_name)
        
        # Return the result
        return JsonResponse(result)
        
    except json.JSONDecodeError as e:
        logger.error(f"MCP API: list_dir_recursively JSON decode error: {e}")
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON payload'
        }, status=400)
    except Exception as e:
        logger.error(f"MCP API: list_dir_recursively unexpected error: {e}")
        return JsonResponse({
            'success': False,
            'error': f'Unexpected error: {str(e)}'
        }, status=500)
