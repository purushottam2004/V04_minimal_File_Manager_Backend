#!/usr/bin/env python3
"""
Test script for File Manager Backend API.
This script tests the main API endpoints to ensure they're working correctly.
"""

import requests
import json
import os
import time

# Configuration
BASE_URL = "http://localhost:8000/api"
TEST_USER = {
    "username": "testuser",
    "password": "testpass123",
    "password2": "testpass123",
    "email": "test@example.com",
    "first_name": "Test",
    "last_name": "User"
}

def print_response(response, title):
    """Print formatted response."""
    print(f"\n{'='*50}")
    print(f"{title}")
    print(f"{'='*50}")
    print(f"Status Code: {response.status_code}")
    try:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"Response: {response.text}")

def test_auth_endpoints():
    """Test authentication endpoints."""
    print("Testing Authentication Endpoints...")
    
    # Test 1: Register new user
    print("\n1. Testing User Registration...")
    response = requests.post(f"{BASE_URL}/auth/register/", json=TEST_USER)
    print_response(response, "User Registration")
    
    if response.status_code == 201:
        print("✅ Registration successful")
    else:
        print("❌ Registration failed")
        return None
    
    # Test 2: Login
    print("\n2. Testing User Login...")
    login_data = {
        "username": TEST_USER["username"],
        "password": TEST_USER["password"]
    }
    response = requests.post(f"{BASE_URL}/auth/login/", json=login_data)
    print_response(response, "User Login")
    
    if response.status_code == 200:
        tokens = response.json()
        access_token = tokens.get('access')
        print("✅ Login successful")
        return access_token
    else:
        print("❌ Login failed")
        return None

def test_user_endpoints(access_token):
    """Test user management endpoints."""
    print("\nTesting User Management Endpoints...")
    
    headers = {"Authorization": f"Bearer {access_token}"}
    
    # Test 1: Get user profile
    print("\n1. Testing Get User Profile...")
    response = requests.get(f"{BASE_URL}/auth/profile/", headers=headers)
    print_response(response, "Get User Profile")
    
    # Test 2: Get user info
    print("\n2. Testing Get User Info...")
    response = requests.get(f"{BASE_URL}/auth/user-info/", headers=headers)
    print_response(response, "Get User Info")
    
    # Test 3: Test auth endpoint
    print("\n3. Testing Auth Test Endpoint...")
    response = requests.post(f"{BASE_URL}/auth/test-auth/", headers=headers)
    print_response(response, "Auth Test")

def test_file_endpoints(access_token):
    """Test file management endpoints."""
    print("\nTesting File Management Endpoints...")
    
    headers = {"Authorization": f"Bearer {access_token}"}
    
    # Test 1: List directory (should be empty initially)
    print("\n1. Testing List Directory...")
    response = requests.get(f"{BASE_URL}/files/list/", headers=headers)
    print_response(response, "List Directory")
    
    # Test 2: Create folder
    print("\n2. Testing Create Folder...")
    folder_data = {
        "parent_path": "",
        "folder_name": "test_folder"
    }
    response = requests.post(f"{BASE_URL}/files/create-folder/", json=folder_data, headers=headers)
    print_response(response, "Create Folder")
    
    # Test 3: List directory again (should show the new folder)
    print("\n3. Testing List Directory (after creating folder)...")
    response = requests.get(f"{BASE_URL}/files/list/", headers=headers)
    print_response(response, "List Directory (Updated)")
    
    # Test 4: Create a test file
    print("\n4. Testing File Upload...")
    test_file_content = "This is a test file content."
    files = {'files': ('test.txt', test_file_content, 'text/plain')}
    data = {'path': 'test_folder'}
    response = requests.post(f"{BASE_URL}/files/upload/", files=files, data=data, headers=headers)
    print_response(response, "File Upload")
    
    # Test 5: List directory in test_folder
    print("\n5. Testing List Directory in test_folder...")
    response = requests.get(f"{BASE_URL}/files/list/?path=test_folder", headers=headers)
    print_response(response, "List Directory in test_folder")
    
    # Test 6: Rename file
    print("\n6. Testing Rename File...")
    rename_data = {
        "old_path": "test_folder\\test.txt",
        "new_name": "renamed_test.txt"
    }
    response = requests.post(f"{BASE_URL}/files/rename/", json=rename_data, headers=headers)
    print_response(response, "Rename File")
    
    # Test 7: Copy file
    print("\n7. Testing Copy File...")
    copy_data = {
        "source_path": "test_folder\\renamed_test.txt",
        "dest_path": ""
    }
    response = requests.post(f"{BASE_URL}/files/copy/", json=copy_data, headers=headers)
    print_response(response, "Copy File")
    
    # Test 8: Move file
    print("\n8. Testing Move File...")
    move_data = {
        "source_path": "renamed_test.txt",
        "dest_path": "test_folder"
    }
    response = requests.post(f"{BASE_URL}/files/move/", json=move_data, headers=headers)
    print_response(response, "Move File")
    
    # Test 9: Final directory listing
    print("\n9. Testing Final Directory Listing...")
    response = requests.get(f"{BASE_URL}/files/list/", headers=headers)
    print_response(response, "Final Directory Listing")
    
    # Test 10: Download file
    print("\n10. Testing File Download...")
    response = requests.get(f"{BASE_URL}/files/download/?path=test_folder\\renamed_test.txt", headers=headers)
    print_response(response, "File Download")
    
    # Test 11: Download ZIP
    print("\n11. Testing ZIP Download...")
    response = requests.get(f"{BASE_URL}/files/download-zip/?path=test_folder", headers=headers)
    print_response(response, "ZIP Download")
    
    # Test 12: Delete file
    print("\n12. Testing Delete File...")
    delete_data = {
        "path": "test_folder\\renamed_test.txt"
    }
    response = requests.post(f"{BASE_URL}/files/delete/", json=delete_data, headers=headers)
    print_response(response, "Delete File")
    
    # Test 13: Delete folder
    print("\n13. Testing Delete Folder...")
    delete_data = {
        "path": "test_folder"
    }
    response = requests.post(f"{BASE_URL}/files/delete/", json=delete_data, headers=headers)
    print_response(response, "Delete Folder")

def main():
    """Main test function."""
    print("🚀 Starting File Manager Backend API Tests")
    print(f"Base URL: {BASE_URL}")
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/auth/test-auth/")
        print("✅ Server is running")
    except requests.exceptions.ConnectionError:
        print("❌ Server is not running. Please start the server first:")
        print("   cd project && uv run python manage.py runserver")
        return
    
    # Test authentication
    access_token = test_auth_endpoints()
    if not access_token:
        print("❌ Authentication tests failed. Stopping.")
        return
    
    # Test user endpoints
    test_user_endpoints(access_token)
    
    # Test file endpoints
    test_file_endpoints(access_token)
    
    print("\n🎉 All tests completed!")
    print("\nTo clean up, you can delete the test user through the admin interface:")
    print("   http://localhost:8000/admin/")

if __name__ == "__main__":
    main() 