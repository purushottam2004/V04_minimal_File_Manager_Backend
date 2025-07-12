"""
Utility functions for MCP API operations.
This module contains functions for Python code execution and directory operations.
"""

import os
import sys
import subprocess
import tempfile
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional
from django.conf import settings
import io
import contextlib

logger = logging.getLogger(settings.MCP_LOGGER)


def execute_python_code(user_dir: str, python_code: str) -> Dict[str, Any]:
    """
    Execute Python code in the user's directory.
    
    Args:
        user_dir (str): The user's directory name in master_dir
        python_code (str): The Python code to execute
        
    Returns:
        Dict[str, Any]: Dictionary containing execution results
    """
    # Debug logging
    if settings.DEBUG:
        logger.debug(f"Executing Python code for user_dir: {user_dir}")
        logger.debug(f"Code length: {len(python_code)} characters")
    
    # Validate user directory
    user_path = Path(settings.MASTER_DIR) / user_dir
    if not user_path.exists():
        logger.error(f"User directory does not exist: {user_path}")
        return {
            'success': False,
            'error': f'User directory "{user_dir}" does not exist',
            'output': '',
            'error_output': ''
        }
    
    # Create a temporary file for the code
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, dir=user_path) as temp_file:
            temp_file.write(python_code)
            temp_file_path = temp_file.name
        
        # Debug logging
        if settings.DEBUG:
            logger.debug(f"Created temporary file: {temp_file_path}")
        
        # Execute the code
        result = _run_python_script(temp_file_path, user_path)
        
        # Clean up temporary file
        try:
            os.unlink(temp_file_path)
            if settings.DEBUG:
                logger.debug(f"Cleaned up temporary file: {temp_file_path}")
        except OSError as e:
            logger.warning(f"Failed to clean up temporary file {temp_file_path}: {e}")
        
        return result
        
    except Exception as e:
        logger.error(f"Error executing Python code: {e}")
        return {
            'success': False,
            'error': f'Failed to execute Python code: {str(e)}',
            'output': '',
            'error_output': ''
        }


def _run_python_script(script_path: str, working_dir: Path) -> Dict[str, Any]:
    """
    Run a Python script in a specific working directory.
    
    Args:
        script_path (str): Path to the Python script
        working_dir (Path): Working directory for execution
        
    Returns:
        Dict[str, Any]: Execution results
    """
    try:
        # Debug logging
        if settings.DEBUG:
            logger.debug(f"Running script: {script_path}")
            logger.debug(f"Working directory: {working_dir}")
        
        # Run the script with timeout and capture output
        result = subprocess.run(
            [sys.executable, script_path],
            cwd=working_dir,
            capture_output=True,
            text=True,
            timeout=30,  # 30 second timeout
            env=os.environ.copy()
        )
        
        # Log execution results
        logger.info(f"Script execution completed with return code: {result.returncode}")
        
        return {
            'success': result.returncode == 0,
            'output': result.stdout,
            'error_output': result.stderr,
            'return_code': result.returncode
        }
        
    except subprocess.TimeoutExpired:
        logger.warning(f"Script execution timed out: {script_path}")
        return {
            'success': False,
            'error': 'Script execution timed out (30 seconds)',
            'output': '',
            'error_output': 'Execution timeout'
        }
    except Exception as e:
        logger.error(f"Error running script {script_path}: {e}")
        return {
            'success': False,
            'error': f'Failed to run script: {str(e)}',
            'output': '',
            'error_output': str(e)
        }


def list_directory(user_dir: str, target_dir: str = '') -> Dict[str, Any]:
    """
    List contents of a directory for a specific user.
    
    Args:
        user_dir (str): The user's directory name in master_dir
        target_dir (str): The directory to list (empty for root)
        
    Returns:
        Dict[str, Any]: Directory listing results
    """
    # Debug logging
    if settings.DEBUG:
        logger.debug(f"Listing directory for user_dir: {user_dir}, target_dir: {target_dir}")
    
    # Validate user directory
    user_path = Path(settings.MASTER_DIR) / user_dir
    if not user_path.exists():
        logger.error(f"User directory does not exist: {user_path}")
        return {
            'success': False,
            'error': f'User directory "{user_dir}" does not exist',
            'items': []
        }
    
    # Build target path
    target_path = user_path / target_dir if target_dir else user_path
    
    # Validate target path
    if not target_path.exists():
        logger.error(f"Target directory does not exist: {target_path}")
        return {
            'success': False,
            'error': f'Target directory "{target_dir}" does not exist',
            'items': []
        }
    
    if not target_path.is_dir():
        logger.error(f"Target path is not a directory: {target_path}")
        return {
            'success': False,
            'error': f'Target path "{target_dir}" is not a directory',
            'items': []
        }
    
    try:
        # List directory contents
        items = []
        for item in target_path.iterdir():
            item_info = {
                'name': item.name,
                'path': str(item.relative_to(user_path)),
                'is_dir': item.is_dir(),
                'is_file': item.is_file(),
                'size': item.stat().st_size if item.is_file() else None
            }
            items.append(item_info)
        
        # Sort items (directories first, then files)
        items.sort(key=lambda x: (not x['is_dir'], x['name'].lower()))
        
        logger.info(f"Successfully listed directory: {target_path} ({len(items)} items)")
        
        return {
            'success': True,
            'items': items,
            'path': str(target_path.relative_to(Path(settings.MASTER_DIR)))
        }
        
    except Exception as e:
        logger.error(f"Error listing directory {target_path}: {e}")
        return {
            'success': False,
            'error': f'Failed to list directory: {str(e)}',
            'items': []
        }


def list_directory_recursively(user_dir: str, target_dir: str = '') -> Dict[str, Any]:
    """
    List contents of a directory recursively for a specific user.
    
    Args:
        user_dir (str): The user's directory name in master_dir
        target_dir (str): The directory to list (empty for root)
        
    Returns:
        Dict[str, Any]: Recursive directory listing results
    """
    # Debug logging
    if settings.DEBUG:
        logger.debug(f"Listing directory recursively for user_dir: {user_dir}, target_dir: {target_dir}")
    
    # Validate user directory
    user_path = Path(settings.MASTER_DIR) / user_dir
    if not user_path.exists():
        logger.error(f"User directory does not exist: {user_path}")
        return {
            'success': False,
            'error': f'User directory "{user_dir}" does not exist',
            'items': []
        }
    
    # Build target path
    target_path = user_path / target_dir if target_dir else user_path
    
    # Validate target path
    if not target_path.exists():
        logger.error(f"Target directory does not exist: {target_path}")
        return {
            'success': False,
            'error': f'Target directory "{target_dir}" does not exist',
            'items': []
        }
    
    if not target_path.is_dir():
        logger.error(f"Target path is not a directory: {target_path}")
        return {
            'success': False,
            'error': f'Target path "{target_dir}" is not a directory',
            'items': []
        }
    
    try:
        # List directory contents recursively
        items = []
        for item in target_path.rglob('*'):
            # Skip the target directory itself
            if item == target_path:
                continue
                
            item_info = {
                'name': item.name,
                'path': str(item.relative_to(user_path)),
                'is_dir': item.is_dir(),
                'is_file': item.is_file(),
                'size': item.stat().st_size if item.is_file() else None,
                'depth': len(item.relative_to(target_path).parts)
            }
            items.append(item_info)
        
        # Sort items by path
        items.sort(key=lambda x: x['path'])
        
        logger.info(f"Successfully listed directory recursively: {target_path} ({len(items)} items)")
        
        return {
            'success': True,
            'items': items,
            'path': str(target_path.relative_to(Path(settings.MASTER_DIR)))
        }
        
    except Exception as e:
        logger.error(f"Error listing directory recursively {target_path}: {e}")
        return {
            'success': False,
            'error': f'Failed to list directory recursively: {str(e)}',
            'items': []
        } 