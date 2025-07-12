"""
URL configuration for MCP API endpoints.
"""

from django.urls import path
from . import views

app_name = 'mcp_api'

urlpatterns = [
    path('run_python_code', views.run_python_code_view, name='run_python_code'),
    path('list_dir', views.list_dir_view, name='list_dir'),
    path('list_dir_recursively', views.list_dir_recursively_view, name='list_dir_recursively'),
] 