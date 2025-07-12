#!/usr/bin/env python3
"""
Quick test to verify copy and move operations work correctly.
"""

import requests
import json

BASE_URL = "http://localhost:8000/api"

def test_copy_move():
    """Test copy and move operations."""
    
    # First, register and login to get a valid token
    print("1. Registering test user...")
    user_data = {
        "username": "quicktest",
        "password": "testpass123",
        "password2": "testpass123",
        "email": "quick@test.com",
        "first_name": "Quick",
        "last_name": "Test"
    }
    
    response = requests.post(f"{BASE_URL}/auth/register/", json=user_data)
    if response.status_code != 201:
        if 'already exists' in response.text:
            print("User already exists, skipping registration.")
        else:
            print(f"Registration failed: {response.text}")
            return
    
    print("2. Logging in...")
    login_data = {
        "username": "quicktest",
        "password": "testpass123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login/", json=login_data)
    if response.status_code != 200:
        print(f"Login failed: {response.text}")
        return
    
    tokens = response.json()
    access_token = tokens['access']
    headers = {"Authorization": f"Bearer {access_token}"}
    
    print("3. Creating test folder...")
    folder_data = {"parent_path": "", "folder_name": "quick_test"}
    response = requests.post(f"{BASE_URL}/files/create-folder/", json=folder_data, headers=headers)
    print(f"Create folder: {response.status_code}")
    
    print("4. Uploading test file...")
    files = {'files': ('testfile.txt', 'This is a test file for copy/move operations.', 'text/plain')}
    data = {'path': 'quick_test'}
    response = requests.post(f"{BASE_URL}/files/upload/", files=files, data=data, headers=headers)
    print(f"Upload file: {response.status_code}")
    
    print("5. Testing copy operation...")
    copy_data = {
        "source_path": "quick_test\\testfile.txt",
        "dest_path": "quick_test"
    }
    response = requests.post(f"{BASE_URL}/files/copy/", json=copy_data, headers=headers)
    print(f"Copy operation: {response.status_code}")
    if response.status_code == 200:
        print(f"Copy response: {response.json()}")
    else:
        print(f"Copy error: {response.text}")
    
    print("6. Testing move operation...")
    move_data = {
        "source_path": "quick_test\\testfile.txt",
        "dest_path": ""
    }
    response = requests.post(f"{BASE_URL}/files/move/", json=move_data, headers=headers)
    print(f"Move operation: {response.status_code}")
    if response.status_code == 200:
        print(f"Move response: {response.json()}")
    else:
        print(f"Move error: {response.text}")
    
    print("7. Listing final directory...")
    response = requests.get(f"{BASE_URL}/files/list/", headers=headers)
    print(f"List directory: {response.status_code}")
    if response.status_code == 200:
        print(f"Directory contents: {response.json()}")
    
    print("✅ Copy and move operations test completed!")

if __name__ == "__main__":
    test_copy_move() 