# MCP API Documentation

## Overview

The MCP (Model Context Protocol) API provides secure endpoints for Python code execution and directory operations. This API is designed for internal use with IP-based authentication.

## Features

- **IP-based Authentication**: Only requests from allowed IP addresses (default: 127.0.0.1) are accepted
- **Python Code Execution**: Execute Python code in user-specific directories
- **Directory Operations**: List directory contents with both regular and recursive options
- **Comprehensive Logging**: All operations are logged with debug support
- **Error Handling**: Robust error handling with detailed error messages

## Configuration

### Environment Variables

```bash
# Allowed IPs for MCP API access (comma-separated)
MCP_ALLOWED_IPS=127.0.0.1,192.168.1.100

# Master directory for user files
MASTER_DIR=/path/to/master_dir

# Debug mode
DEBUG=True
```

### Settings

The MCP API is configured in `project/project/settings.py`:

```python
# MCP API Settings
MCP_ALLOWED_IPS = config('MCP_ALLOWED_IPS', default='127.0.0.1', cast=lambda v: [s.strip() for s in v.split(',')])
MCP_LOGGER = 'mcp_api'
```

## API Endpoints

### 1. Execute Python Code

**Endpoint:** `POST /mcp_api/run_python_code`

**Description:** Execute Python code in a user's directory.

**Request Body:**
```json
{
    "user_dir": "user_directory_name",
    "python_code": "print('Hello, World!')"
}
```

**Response:**
```json
{
    "success": true,
    "output": "Hello, World!\n",
    "error_output": "",
    "return_code": 0
}
```

**Error Response:**
```json
{
    "success": false,
    "error": "User directory 'invalid_user' does not exist",
    "output": "",
    "error_output": ""
}
```

### 2. List Directory

**Endpoint:** `POST /mcp_api/list_dir`

**Description:** List contents of a directory for a specific user.

**Request Body:**
```json
{
    "user_dir": "user_directory_name",
    "dir_name": "optional_subdirectory"
}
```

**Response:**
```json
{
    "success": true,
    "items": [
        {
            "name": "file1.txt",
            "path": "file1.txt",
            "is_dir": false,
            "is_file": true,
            "size": 1024
        },
        {
            "name": "subdir",
            "path": "subdir",
            "is_dir": true,
            "is_file": false,
            "size": null
        }
    ],
    "path": "user_directory_name"
}
```

### 3. List Directory Recursively

**Endpoint:** `POST /mcp_api/list_dir_recursively`

**Description:** List contents of a directory recursively for a specific user.

**Request Body:**
```json
{
    "user_dir": "user_directory_name",
    "dir_name": "optional_subdirectory"
}
```

**Response:**
```json
{
    "success": true,
    "items": [
        {
            "name": "file1.txt",
            "path": "file1.txt",
            "is_dir": false,
            "is_file": true,
            "size": 1024,
            "depth": 0
        },
        {
            "name": "file2.txt",
            "path": "subdir/file2.txt",
            "is_dir": false,
            "is_file": true,
            "size": 512,
            "depth": 1
        }
    ],
    "path": "user_directory_name"
}
```

## Security Features

### IP Authentication

The MCP API uses IP-based authentication through middleware. Only requests from allowed IP addresses are processed.

**Middleware:** `mcp_api.middleware.MCPIPAuthenticationMiddleware`

**Features:**
- Checks client IP against allowed IPs list
- Supports X-Forwarded-For header for proxy scenarios
- Logs all authentication attempts
- Returns 403 Forbidden for unauthorized IPs

### Code Execution Safety

- **Timeout Protection**: Code execution is limited to 30 seconds
- **Working Directory Isolation**: Code runs in user-specific directories
- **Temporary File Cleanup**: Temporary files are automatically cleaned up
- **Error Capture**: All stdout/stderr is captured and returned

## Error Handling

All endpoints return consistent error responses:

```json
{
    "success": false,
    "error": "Error description"
}
```

**Common Error Scenarios:**
- Invalid JSON payload
- Missing required fields
- Invalid data types
- Non-existent user directories
- Non-existent target directories
- Code execution timeouts
- File system errors

## Logging

The MCP API provides comprehensive logging:

**Log Levels:**
- **DEBUG**: Detailed operation information (when DEBUG=True)
- **INFO**: General operation logs
- **WARNING**: Security warnings and non-critical issues
- **ERROR**: Error conditions and failures

**Log Format:**
```
{levelname} {asctime} {module} {process:d} {thread:d} {message}
```

**Log Files:**
- Console output
- File: `project/logs/django.log`

## Usage Examples

### Python Code Execution

```python
import requests

url = "http://127.0.0.1:8000/mcp_api/run_python_code"
payload = {
    "user_dir": "my_user",
    "python_code": """
import os
print(f"Current directory: {os.getcwd()}")
print(f"Files in directory: {os.listdir('.')}")
"""
}

response = requests.post(url, json=payload)
result = response.json()
print(result)
```

### Directory Listing

```python
import requests

url = "http://127.0.0.1:8000/mcp_api/list_dir"
payload = {
    "user_dir": "my_user",
    "dir_name": "documents"
}

response = requests.post(url, json=payload)
result = response.json()
print(result)
```

## Testing

Use the provided test script to verify functionality:

```bash
# Start the Django server
uv run python project/manage.py runserver

# Run tests
python test_mcp_api.py
```

## File Structure

```
project/
├── mcp_api/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── middleware.py      # IP authentication middleware
│   ├── models.py
│   ├── tests.py
│   ├── urls.py           # URL patterns
│   ├── utils.py          # Utility functions
│   └── views.py          # API views
├── master_dir/           # User directories
│   └── test_user/
└── project/
    ├── settings.py       # Django settings
    └── urls.py          # Main URL configuration
```

## Dependencies

- Django 5.2+
- Python 3.8+
- requests (for testing)

## Security Considerations

1. **IP Whitelisting**: Only allow trusted IP addresses
2. **Code Execution**: Monitor and limit code execution time
3. **Directory Access**: Validate all directory paths
4. **Logging**: Monitor logs for suspicious activity
5. **Error Messages**: Avoid exposing sensitive information in error messages

## Troubleshooting

### Common Issues

1. **403 Forbidden**: Check if your IP is in the allowed list
2. **404 Not Found**: Verify the endpoint URL is correct
3. **400 Bad Request**: Check JSON payload format and required fields
4. **500 Internal Server Error**: Check server logs for details

### Debug Mode

Enable debug mode for detailed logging:

```bash
export DEBUG=True
```

This will provide additional debug information in logs and responses. 