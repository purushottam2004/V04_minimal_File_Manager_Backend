# File Manager Backend

A Django REST API backend for a secure file management system with JWT authentication and role-based access control.

## Features

- **JWT Authentication**: Secure token-based authentication system
- **Role-based Access Control**: Superuser, Manager, and Normal User roles
- **Directory Isolation**: Users can only access their assigned directories
- **File Operations**: Upload, download, delete, rename, move, copy files and folders
- **ZIP Support**: Download directories as ZIP files
- **Security**: Path validation to prevent directory traversal attacks
- **Logging**: Comprehensive logging for debugging and monitoring

## Technology Stack

- **Backend**: Django 5.2.4
- **API**: Django REST Framework
- **Authentication**: JWT (JSON Web Tokens)
- **Database**: SQLite3
- **Environment Management**: uv
- **Python Version**: 3.11+

## Project Structure

```
BACKEND/
├── project/                    # Django project directory
│   ├── auth_app/              # Authentication and user management
│   │   ├── models.py          # UserProfile model
│   │   ├── serializers.py     # API serializers
│   │   ├── views.py           # API views
│   │   ├── urls.py            # URL routing
│   │   └── admin.py           # Admin interface
│   ├── file_manager_core/     # File management operations
│   │   ├── views.py           # File operation views
│   │   └── urls.py            # URL routing
│   ├── project/               # Django settings
│   │   ├── settings.py        # Project configuration
│   │   └── urls.py            # Main URL routing
│   ├── master_dir/            # User file storage
│   ├── logs/                  # Application logs
│   └── manage.py              # Django management
├── .venv/                     # Virtual environment
├── pyproject.toml             # Project dependencies
├── API_DOCUMENTATION.md       # Complete API documentation
├── test_api.py                # API testing script
└── README.md                  # This file
```

## Quick Start

### Prerequisites

- Python 3.11 or higher
- uv package manager

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd BACKEND
   ```

2. **Activate virtual environment**
   ```bash
   ./.venv/Scripts/Activate
   ```

3. **Install dependencies**
   ```bash
   uv sync
   ```

4. **Run migrations**
   ```bash
   cd project
   uv run python manage.py migrate
   ```

5. **Create superuser**
   ```bash
   uv run python manage.py createsuperuser
   ```

6. **Start the server**
   ```bash
   uv run python manage.py runserver
   ```

The API will be available at `http://localhost:8000/api/`

## API Endpoints

### Authentication
- `POST /api/auth/register/` - User registration
- `POST /api/auth/login/` - User login
- `POST /api/auth/token/refresh/` - Refresh JWT token
- `POST /api/auth/logout/` - User logout

### User Management
- `GET /api/auth/profile/` - Get user profile
- `PUT/PATCH /api/auth/profile/` - Update user profile
- `POST /api/auth/change-password/` - Change password
- `GET /api/auth/user-info/` - Get user information
- `GET /api/auth/users/` - List users (managers/superusers only)

### File Operations
- `GET /api/files/list/` - List directory contents
- `POST /api/files/upload/` - Upload files
- `GET /api/files/download/` - Download file
- `GET /api/files/download-zip/` - Download directory as ZIP
- `POST /api/files/create-folder/` - Create folder
- `POST /api/files/delete/` - Delete file/folder
- `POST /api/files/rename/` - Rename file/folder
- `POST /api/files/move/` - Move file/folder
- `POST /api/files/copy/` - Copy file/folder

## User Roles

### Superuser
- Full access to all features
- Can manage all users and their profiles
- Can access admin interface

### Manager
- Can manage users (view user list)
- Can perform all file operations
- Cannot access admin interface

### Normal User
- Can only access their own directory
- Can perform file operations within their directory
- Cannot manage other users

## Security Features

1. **JWT Authentication**: Secure token-based authentication
2. **Directory Isolation**: Users can only access their assigned directories
3. **Path Validation**: All file operations validate paths to prevent directory traversal
4. **Role-based Access**: Different permissions for different user types
5. **Input Validation**: All inputs are validated and sanitized

## File Structure

```
master_dir/
├── user_admin_1/              # Superuser directory
│   ├── documents/
│   └── files/
├── user_john_doe_2/           # Normal user directory
│   ├── work/
│   └── personal/
└── user_manager_3/            # Manager directory
    └── projects/
```

Each user has their own isolated directory within the master directory, ensuring complete separation of user data.

## Testing

Run the test script to verify all API endpoints:

```bash
python test_api.py
```

This will test:
- User registration and login
- Profile management
- File operations (create, upload, download, rename, move, copy, delete)
- Directory operations

## Admin Interface

Access the Django admin interface at `http://localhost:8000/admin/` to manage users and their profiles.

Default superuser credentials:
- Username: `admin`
- Password: `admin123`

## Environment Variables

Create a `.env` file in the project root for custom configuration:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
MASTER_DIR=/path/to/master/directory
```

## Logging

The application includes comprehensive logging:
- Console output for development
- File logging in `project/logs/django.log`
- Different log levels for different components
- Debug logging when `DEBUG=True`

## API Documentation

For detailed API documentation with examples, see [API_DOCUMENTATION.md](API_DOCUMENTATION.md).

## Contributing

1. Follow the existing code style
2. Add comments and docstrings to all functions
3. Include type hints for function arguments and return types
4. Add logging statements for debugging
5. Test your changes thoroughly

## License

This project is licensed under the MIT License.

