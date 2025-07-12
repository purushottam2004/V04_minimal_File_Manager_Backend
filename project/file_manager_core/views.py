"""
Views for file manager core app - file and folder operations.
"""
import os
import shutil
import zipfile
import tempfile
from pathlib import Path
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser, FileUploadParser
import logging

logger = logging.getLogger(__name__)


def get_user_directory(user) -> str:
    """
    Get the user's assigned directory path.
    
    Args:
        user: Django User instance
        
    Returns:
        str: Full path to user's directory
        
    Raises:
        ValueError: If user has no profile or directory
    """
    try:
        profile = user.profile
        user_dir = os.path.join(settings.MASTER_DIR, profile.dir_name)
        
        # Create directory if it doesn't exist
        os.makedirs(user_dir, exist_ok=True)
        
        return user_dir
    except Exception as e:
        logger.error(f"Error getting user directory for {user.username}: {str(e)}")
        raise ValueError(f"User directory not found: {str(e)}")


def validate_path_security(user_dir: str, target_path: str) -> str:
    """
    Validate that the target path is within the user's directory.
    
    Args:
        user_dir: User's base directory
        target_path: Path to validate
        
    Returns:
        str: Resolved absolute path
        
    Raises:
        ValueError: If path is outside user's directory
    """
    # Resolve the target path
    resolved_path = os.path.abspath(target_path)
    user_dir_abs = os.path.abspath(user_dir)
    
    # Check if the resolved path is within the user's directory
    if not resolved_path.startswith(user_dir_abs):
        logger.warning(f"Security violation: {target_path} is outside user directory {user_dir}")
        raise ValueError("Access denied: Path is outside your directory")
    
    return resolved_path


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def list_directory(request):
    """
    List contents of a directory.
    
    Returns files and folders in the specified directory.
    """
    try:
        user = request.user
        user_dir = get_user_directory(user)
        
        # Get the target directory (default to user's root directory)
        target_dir = request.GET.get('path', '')
        if target_dir:
            full_path = os.path.join(user_dir, target_dir)
            full_path = validate_path_security(user_dir, full_path)
        else:
            full_path = user_dir
        
        if not os.path.exists(full_path):
            return Response({
                'error': 'Directory not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        if not os.path.isdir(full_path):
            return Response({
                'error': 'Path is not a directory'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # List directory contents
        items = []
        for item in os.listdir(full_path):
            item_path = os.path.join(full_path, item)
            item_info = {
                'name': item,
                'is_directory': os.path.isdir(item_path),
                'size': os.path.getsize(item_path) if os.path.isfile(item_path) else None,
                'modified': os.path.getmtime(item_path),
            }
            items.append(item_info)
        
        # Sort: directories first, then files
        items.sort(key=lambda x: (not x['is_directory'], x['name'].lower()))
        
        logger.info(f"Directory listed for user {user.username}: {full_path}")
        return Response({
            'path': target_dir,
            'items': items,
            'total_items': len(items)
        })
        
    except ValueError as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_403_FORBIDDEN)
    except Exception as e:
        logger.error(f"Error listing directory for {request.user.username}: {str(e)}")
        return Response({
            'error': 'Failed to list directory',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def upload_file(request):
    """
    Upload a file to the user's directory.
    
    Accepts single or multiple files.
    """
    try:
        user = request.user
        user_dir = get_user_directory(user)
        
        # Get target directory
        target_dir = request.POST.get('path', '')
        if target_dir:
            upload_path = os.path.join(user_dir, target_dir)
            upload_path = validate_path_security(user_dir, upload_path)
        else:
            upload_path = user_dir
        
        # Ensure upload directory exists
        os.makedirs(upload_path, exist_ok=True)
        
        uploaded_files = []
        files = request.FILES.getlist('files')
        
        if not files:
            return Response({
                'error': 'No files provided'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        for file in files:
            try:
                # Validate file name
                if not file.name or file.name.strip() == '':
                    continue
                
                # Create file path
                file_path = os.path.join(upload_path, file.name)
                
                # Check if file already exists
                if os.path.exists(file_path):
                    return Response({
                        'error': f'File {file.name} already exists'
                    }, status=status.HTTP_409_CONFLICT)
                
                # Save file
                with open(file_path, 'wb+') as destination:
                    for chunk in file.chunks():
                        destination.write(chunk)
                
                uploaded_files.append({
                    'name': file.name,
                    'size': file.size,
                    'path': os.path.relpath(file_path, user_dir)
                })
                
                logger.info(f"File uploaded by {user.username}: {file_path}")
                
            except Exception as e:
                logger.error(f"Error uploading file {file.name} for {user.username}: {str(e)}")
                return Response({
                    'error': f'Failed to upload {file.name}',
                    'details': str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response({
            'message': f'Successfully uploaded {len(uploaded_files)} files',
            'files': uploaded_files
        }, status=status.HTTP_201_CREATED)
        
    except ValueError as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_403_FORBIDDEN)
    except Exception as e:
        logger.error(f"Error in upload_file for {request.user.username}: {str(e)}")
        return Response({
            'error': 'Upload failed',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def download_file(request):
    """
    Download a file from the user's directory.
    
    Supports single file download.
    """
    try:
        user = request.user
        user_dir = get_user_directory(user)
        
        # Get file path
        file_path = request.GET.get('path', '')
        if not file_path:
            return Response({
                'error': 'File path not provided'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        full_path = os.path.join(user_dir, file_path)
        full_path = validate_path_security(user_dir, full_path)
        
        if not os.path.exists(full_path):
            return Response({
                'error': 'File not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        if not os.path.isfile(full_path):
            return Response({
                'error': 'Path is not a file'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Read and return file
        with open(full_path, 'rb') as file:
            response = HttpResponse(file.read(), content_type='application/octet-stream')
            response['Content-Disposition'] = f'attachment; filename="{os.path.basename(full_path)}"'
        
        logger.info(f"File downloaded by {user.username}: {full_path}")
        return response
        
    except ValueError as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_403_FORBIDDEN)
    except Exception as e:
        logger.error(f"Error downloading file for {request.user.username}: {str(e)}")
        return Response({
            'error': 'Download failed',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def delete_item(request):
    """
    Delete a file or folder.
    
    Supports recursive deletion of directories.
    """
    try:
        user = request.user
        user_dir = get_user_directory(user)
        
        # Get item path
        item_path = request.data.get('path', '')
        if not item_path:
            return Response({
                'error': 'Item path not provided'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        full_path = os.path.join(user_dir, item_path)
        full_path = validate_path_security(user_dir, full_path)
        
        if not os.path.exists(full_path):
            return Response({
                'error': 'Item not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Delete item
        if os.path.isdir(full_path):
            shutil.rmtree(full_path)
            logger.info(f"Directory deleted by {user.username}: {full_path}")
        else:
            os.remove(full_path)
            logger.info(f"File deleted by {user.username}: {full_path}")
        
        return Response({
            'message': 'Item deleted successfully'
        }, status=status.HTTP_200_OK)
        
    except ValueError as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_403_FORBIDDEN)
    except Exception as e:
        logger.error(f"Error deleting item for {request.user.username}: {str(e)}")
        return Response({
            'error': 'Delete failed',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def rename_item(request):
    """
    Rename a file or folder.
    """
    try:
        user = request.user
        user_dir = get_user_directory(user)
        
        # Get old and new names
        old_path = request.data.get('old_path', '')
        new_name = request.data.get('new_name', '')
        
        if not old_path or not new_name:
            return Response({
                'error': 'Old path and new name are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        old_full_path = os.path.join(user_dir, old_path)
        old_full_path = validate_path_security(user_dir, old_full_path)
        
        if not os.path.exists(old_full_path):
            return Response({
                'error': 'Item not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Create new path
        new_path = os.path.join(os.path.dirname(old_full_path), new_name)
        new_path = validate_path_security(user_dir, new_path)
        
        if os.path.exists(new_path):
            return Response({
                'error': 'Item with new name already exists'
            }, status=status.HTTP_409_CONFLICT)
        
        # Rename item
        os.rename(old_full_path, new_path)
        
        logger.info(f"Item renamed by {user.username}: {old_full_path} -> {new_path}")
        return Response({
            'message': 'Item renamed successfully',
            'new_path': os.path.relpath(new_path, user_dir)
        }, status=status.HTTP_200_OK)
        
    except ValueError as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_403_FORBIDDEN)
    except Exception as e:
        logger.error(f"Error renaming item for {request.user.username}: {str(e)}")
        return Response({
            'error': 'Rename failed',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def move_item(request):
    """
    Move a file or folder to a different location.
    """
    try:
        user = request.user
        user_dir = get_user_directory(user)
        
        # Get source and destination paths
        source_path = request.data.get('source_path', '')
        dest_path = request.data.get('dest_path', '')
        
        if not source_path or not dest_path:
            return Response({
                'error': 'Source and destination paths are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        source_full_path = os.path.join(user_dir, source_path)
        source_full_path = validate_path_security(user_dir, source_full_path)
        
        # Handle destination path (empty string means root directory)
        if dest_path:
            dest_full_path = os.path.join(user_dir, dest_path)
            dest_full_path = validate_path_security(user_dir, dest_full_path)
        else:
            dest_full_path = user_dir
        
        if not os.path.exists(source_full_path):
            return Response({
                'error': 'Source item not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        if not os.path.exists(dest_full_path) or not os.path.isdir(dest_full_path):
            return Response({
                'error': 'Destination directory not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Create destination path
        final_dest_path = os.path.join(dest_full_path, os.path.basename(source_full_path))
        
        if os.path.exists(final_dest_path):
            return Response({
                'error': 'Item with same name already exists in destination'
            }, status=status.HTTP_409_CONFLICT)
        
        # Move item
        shutil.move(source_full_path, final_dest_path)
        
        logger.info(f"Item moved by {user.username}: {source_full_path} -> {final_dest_path}")
        return Response({
            'message': 'Item moved successfully',
            'new_path': os.path.relpath(final_dest_path, user_dir)
        }, status=status.HTTP_200_OK)
        
    except ValueError as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_403_FORBIDDEN)
    except Exception as e:
        logger.error(f"Error moving item for {request.user.username}: {str(e)}")
        return Response({
            'error': 'Move failed',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def copy_item(request):
    """
    Copy a file or folder to a different location.
    """
    try:
        user = request.user
        user_dir = get_user_directory(user)
        
        # Get source and destination paths
        source_path = request.data.get('source_path', '')
        dest_path = request.data.get('dest_path', '')
        
        if not source_path or not dest_path:
            return Response({
                'error': 'Source and destination paths are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        source_full_path = os.path.join(user_dir, source_path)
        source_full_path = validate_path_security(user_dir, source_full_path)
        
        # Handle destination path (empty string means root directory)
        if dest_path:
            dest_full_path = os.path.join(user_dir, dest_path)
            dest_full_path = validate_path_security(user_dir, dest_full_path)
        else:
            dest_full_path = user_dir
        
        if not os.path.exists(source_full_path):
            return Response({
                'error': 'Source item not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        if not os.path.exists(dest_full_path) or not os.path.isdir(dest_full_path):
            return Response({
                'error': 'Destination directory not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Create destination path
        final_dest_path = os.path.join(dest_full_path, os.path.basename(source_full_path))
        
        if os.path.exists(final_dest_path):
            return Response({
                'error': 'Item with same name already exists in destination'
            }, status=status.HTTP_409_CONFLICT)
        
        # Copy item
        if os.path.isdir(source_full_path):
            shutil.copytree(source_full_path, final_dest_path)
        else:
            shutil.copy2(source_full_path, final_dest_path)
        
        logger.info(f"Item copied by {user.username}: {source_full_path} -> {final_dest_path}")
        return Response({
            'message': 'Item copied successfully',
            'new_path': os.path.relpath(final_dest_path, user_dir)
        }, status=status.HTTP_200_OK)
        
    except ValueError as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_403_FORBIDDEN)
    except Exception as e:
        logger.error(f"Error copying item for {request.user.username}: {str(e)}")
        return Response({
            'error': 'Copy failed',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def create_folder(request):
    """
    Create a new folder.
    """
    try:
        user = request.user
        user_dir = get_user_directory(user)
        
        # Get folder path and name
        parent_path = request.data.get('parent_path', '')
        folder_name = request.data.get('folder_name', '')
        
        if not folder_name:
            return Response({
                'error': 'Folder name is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if parent_path:
            parent_full_path = os.path.join(user_dir, parent_path)
            parent_full_path = validate_path_security(user_dir, parent_full_path)
        else:
            parent_full_path = user_dir
        
        # Create folder path
        folder_path = os.path.join(parent_full_path, folder_name)
        folder_path = validate_path_security(user_dir, folder_path)
        
        if os.path.exists(folder_path):
            return Response({
                'error': 'Folder already exists'
            }, status=status.HTTP_409_CONFLICT)
        
        # Create folder
        os.makedirs(folder_path)
        
        logger.info(f"Folder created by {user.username}: {folder_path}")
        return Response({
            'message': 'Folder created successfully',
            'folder_path': os.path.relpath(folder_path, user_dir)
        }, status=status.HTTP_201_CREATED)
        
    except ValueError as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_403_FORBIDDEN)
    except Exception as e:
        logger.error(f"Error creating folder for {request.user.username}: {str(e)}")
        return Response({
            'error': 'Failed to create folder',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def download_zip(request):
    """
    Download a folder as a ZIP file.
    """
    try:
        user = request.user
        user_dir = get_user_directory(user)
        
        # Get folder path
        folder_path = request.GET.get('path', '')
        if not folder_path:
            return Response({
                'error': 'Folder path not provided'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        full_path = os.path.join(user_dir, folder_path)
        full_path = validate_path_security(user_dir, full_path)
        
        if not os.path.exists(full_path):
            return Response({
                'error': 'Folder not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        if not os.path.isdir(full_path):
            return Response({
                'error': 'Path is not a folder'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Create temporary ZIP file
        with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as temp_zip:
            with zipfile.ZipFile(temp_zip.name, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(full_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arc_name = os.path.relpath(file_path, full_path)
                        zipf.write(file_path, arc_name)
        
        # Read and return ZIP file
        with open(temp_zip.name, 'rb') as zip_file:
            response = HttpResponse(zip_file.read(), content_type='application/zip')
            response['Content-Disposition'] = f'attachment; filename="{os.path.basename(full_path)}.zip"'
        
        # Clean up temporary file
        os.unlink(temp_zip.name)
        
        logger.info(f"Folder downloaded as ZIP by {user.username}: {full_path}")
        return response
        
    except ValueError as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_403_FORBIDDEN)
    except Exception as e:
        logger.error(f"Error downloading ZIP for {request.user.username}: {str(e)}")
        return Response({
            'error': 'ZIP download failed',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
