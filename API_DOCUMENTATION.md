# File Manager Backend API Documentation

## Overview

This is a Django REST API backend for a file management system with JWT authentication and role-based access control. Users can only access their assigned directories and perform various file operations.

## Base URL
```
http://localhost:8000/api/
```

## Authentication

All API endpoints (except registration and login) require JWT authentication. Include the token in the Authorization header:

```
Authorization: Bearer <your_access_token>
```

## User Roles

- **Superuser**: Full access to all features and user management
- **Manager**: Can manage users and access all file operations
- **Normal User**: Can only access their own directory and perform file operations

## API Endpoints

### Authentication Endpoints

#### 1. User Registration
**POST** `/auth/register/`

Register a new user account.

**Request Body:**
```json
{
    "username": "john_doe",
    "password": "securepassword123",
    "password2": "securepassword123",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe"
}
```

**Response:**
```json
{
    "message": "User registered successfully",
    "user_id": 2,
    "username": "john_doe",
    "dir_name": "user_john_doe_2"
}
```

#### 2. User Login
**POST** `/auth/login/`

Authenticate user and get JWT tokens.

**Request Body:**
```json
{
    "username": "john_doe",
    "password": "securepassword123"
}
```

**Response:**
```json
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "user_id": 2,
    "username": "john_doe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "is_superuser": false,
    "is_staff": false,
    "is_manager": false,
    "is_normal_user": true,
    "user_type": "normal",
    "dir_name": "user_john_doe_2",
    "full_name": "John Doe"
}
```

#### 3. Token Refresh
**POST** `/auth/token/refresh/`

Refresh the access token using a refresh token.

**Request Body:**
```json
{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Response:**
```json
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

#### 4. User Logout
**POST** `/auth/logout/`

Logout user by blacklisting the refresh token.

**Request Body:**
```json
{
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Response:**
```json
{
    "message": "Logged out successfully"
}
```

### User Management Endpoints

#### 5. Get User Profile
**GET** `/auth/profile/`

Get current user's profile information.

**Response:**
```json
{
    "id": 2,
    "username": "john_doe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "is_superuser": false,
    "is_staff": false,
    "is_manager": false,
    "is_normal_user": true,
    "user_type": "normal",
    "dir_name": "user_john_doe_2",
    "full_name": "John Doe",
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
}
```

#### 6. Update User Profile
**PUT/PATCH** `/auth/profile/`

Update current user's profile information.

**Request Body:**
```json
{
    "first_name": "Johnny",
    "last_name": "Smith"
}
```

#### 7. Change Password
**POST** `/auth/change-password/`

Change user's password.

**Request Body:**
```json
{
    "old_password": "oldpassword123",
    "new_password": "newpassword123",
    "new_password2": "newpassword123"
}
```

**Response:**
```json
{
    "message": "Password changed successfully"
}
```

#### 8. Get User Info
**GET** `/auth/user-info/`

Get detailed information about the current user.

**Response:**
```json
{
    "user_id": 2,
    "username": "john_doe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "is_superuser": false,
    "is_staff": false,
    "is_manager": false,
    "is_normal_user": true,
    "user_type": "normal",
    "dir_name": "user_john_doe_2",
    "full_name": "John Doe",
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
}
```

#### 9. List Users (Managers/Superusers Only)
**GET** `/auth/users/`

Get list of all users (requires manager or superuser permissions).

**Response:**
```json
[
    {
        "id": 1,
        "username": "admin",
        "email": "admin@example.com",
        "first_name": "Admin",
        "last_name": "User",
        "is_superuser": true,
        "is_staff": true,
        "is_manager": false,
        "is_normal_user": false,
        "user_type": "superuser",
        "dir_name": "user_admin_1",
        "full_name": "Admin User",
        "created_at": "2024-01-15T10:00:00Z",
        "updated_at": "2024-01-15T10:00:00Z"
    }
]
```

### File Management Endpoints

#### 10. List Directory Contents
**GET** `/files/list/`

List files and folders in a directory.

**Query Parameters:**
- `path` (optional): Relative path to the directory (default: root directory)

**Response:**
```json
{
    "path": "",
    "items": [
        {
            "name": "documents",
            "is_directory": true,
            "size": null,
            "modified": 1705312200.0
        },
        {
            "name": "report.pdf",
            "is_directory": false,
            "size": 1024000,
            "modified": 1705312000.0
        }
    ],
    "total_items": 2
}
```

#### 11. Upload Files
**POST** `/files/upload/`

Upload one or more files to a directory.

**Form Data:**
- `files`: File(s) to upload
- `path` (optional): Target directory path

**Response:**
```json
{
    "message": "Successfully uploaded 2 files",
    "files": [
        {
            "name": "document1.pdf",
            "size": 1024000,
            "path": "documents/document1.pdf"
        },
        {
            "name": "image.jpg",
            "size": 512000,
            "path": "documents/image.jpg"
        }
    ]
}
```

#### 12. Download File
**GET** `/files/download/`

Download a single file.

**Query Parameters:**
- `path`: Path to the file relative to user's directory

**Response:** File download

#### 13. Download Directory as ZIP
**GET** `/files/download-zip/`

Download a directory as a ZIP file.

**Query Parameters:**
- `path`: Path to the directory relative to user's directory

**Response:** ZIP file download

#### 14. Create Folder
**POST** `/files/create-folder/`

Create a new folder.

**Request Body:**
```json
{
    "parent_path": "documents",
    "folder_name": "new_folder"
}
```

**Response:**
```json
{
    "message": "Folder created successfully",
    "folder_path": "documents/new_folder"
}
```

#### 15. Delete Item
**POST** `/files/delete/`

Delete a file or folder.

**Request Body:**
```json
{
    "path": "documents/old_file.txt"
}
```

**Response:**
```json
{
    "message": "Item deleted successfully"
}
```

#### 16. Rename Item
**POST** `/files/rename/`

Rename a file or folder.

**Request Body:**
```json
{
    "old_path": "documents/old_name.txt",
    "new_name": "new_name.txt"
}
```

**Response:**
```json
{
    "message": "Item renamed successfully",
    "new_path": "documents/new_name.txt"
}
```

#### 17. Move Item
**POST** `/files/move/`

Move a file or folder to a different location.

**Request Body:**
```json
{
    "source_path": "documents/file.txt",
    "dest_path": "archive"
}
```

**Response:**
```json
{
    "message": "Item moved successfully",
    "new_path": "archive/file.txt"
}
```

#### 18. Copy Item
**POST** `/files/copy/`

Copy a file or folder to a different location.

**Request Body:**
```json
{
    "source_path": "documents/file.txt",
    "dest_path": "backup"
}
```

**Response:**
```json
{
    "message": "Item copied successfully",
    "new_path": "backup/file.txt"
}
```

## Error Responses

All endpoints return consistent error responses:

```json
{
    "error": "Error message",
    "details": "Detailed error information (optional)"
}
```

Common HTTP status codes:
- `200`: Success
- `201`: Created
- `400`: Bad Request
- `401`: Unauthorized
- `403`: Forbidden
- `404`: Not Found
- `409`: Conflict
- `500`: Internal Server Error

## Security Features

1. **JWT Authentication**: Secure token-based authentication
2. **Directory Isolation**: Users can only access their assigned directories
3. **Path Validation**: All file operations validate paths to prevent directory traversal
4. **Role-based Access**: Different permissions for different user types
5. **Input Validation**: All inputs are validated and sanitized

## Usage Examples

### Python Example (requests library)

```python
import requests

# Base URL
BASE_URL = "http://localhost:8000/api"

# Register a new user
register_data = {
    "username": "testuser",
    "password": "testpass123",
    "password2": "testpass123",
    "email": "test@example.com",
    "first_name": "Test",
    "last_name": "User"
}

response = requests.post(f"{BASE_URL}/auth/register/", json=register_data)
print(response.json())

# Login
login_data = {
    "username": "testuser",
    "password": "testpass123"
}

response = requests.post(f"{BASE_URL}/auth/login/", json=login_data)
tokens = response.json()
access_token = tokens['access']

# Set up headers for authenticated requests
headers = {
    "Authorization": f"Bearer {access_token}"
}

# List directory contents
response = requests.get(f"{BASE_URL}/files/list/", headers=headers)
print(response.json())

# Upload a file
files = {'files': open('test.txt', 'rb')}
data = {'path': 'documents'}
response = requests.post(f"{BASE_URL}/files/upload/", files=files, data=data, headers=headers)
print(response.json())
```

### JavaScript Example (fetch API)

```javascript
const BASE_URL = "http://localhost:8000/api";

// Login
async function login(username, password) {
    const response = await fetch(`${BASE_URL}/auth/login/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, password })
    });
    return response.json();
}

// List directory
async function listDirectory(token, path = '') {
    const response = await fetch(`${BASE_URL}/files/list/?path=${path}`, {
        headers: {
            'Authorization': `Bearer ${token}`
        }
    });
    return response.json();
}

// Usage
login('testuser', 'testpass123').then(data => {
    const token = data.access;
    listDirectory(token).then(files => {
        console.log(files);
    });
});
```

## Environment Variables

Create a `.env` file in the project root:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
MASTER_DIR=/path/to/master/directory
```

## Admin Interface

Access the Django admin interface at `http://localhost:8000/admin/` to manage users and their profiles.

Default superuser credentials:
- Username: `admin`
- Password: `admin123`

## File Structure

```
master_dir/
├── user_admin_1/
│   ├── documents/
│   └── files/
├── user_john_doe_2/
│   ├── work/
│   └── personal/
└── user_manager_3/
    └── projects/
```

Each user has their own isolated directory within the master directory, ensuring complete separation of user data. 