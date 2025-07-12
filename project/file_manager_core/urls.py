"""
URL patterns for file manager core app.
"""
from django.urls import path

from .views import (
    list_directory,
    upload_file,
    download_file,
    delete_item,
    rename_item,
    move_item,
    copy_item,
    create_folder,
    download_zip
)

app_name = 'file_manager_core'

urlpatterns = [
    # Directory operations
    path('list/', list_directory, name='list_directory'),
    path('create-folder/', create_folder, name='create_folder'),
    
    # File operations
    path('upload/', upload_file, name='upload_file'),
    path('download/', download_file, name='download_file'),
    path('download-zip/', download_zip, name='download_zip'),
    
    # Item operations
    path('delete/', delete_item, name='delete_item'),
    path('rename/', rename_item, name='rename_item'),
    path('move/', move_item, name='move_item'),
    path('copy/', copy_item, name='copy_item'),
] 