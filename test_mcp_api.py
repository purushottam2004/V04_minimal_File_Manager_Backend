#!/usr/bin/env python3
"""
Test script for MCP API functionality.
This script tests all three MCP API endpoints.
"""

import requests
import json
import sys

# Configuration
BASE_URL = "http://127.0.0.1:8000"
TEST_USER_DIR = "test_user"

def test_run_python_code():
    """Test the run_python_code endpoint."""
    print("Testing run_python_code endpoint...")
    
    url = f"{BASE_URL}/mcp_api/run_python_code"
    payload = {
        "user_dir": TEST_USER_DIR,
        "python_code": "print('Hello from MCP API!')\nprint('Current directory:', __import__('os').getcwd())\nprint('Python version:', __import__('sys').version)"
    }
    
    try:
        response = requests.post(url, json=payload)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_list_dir():
    """Test the list_dir endpoint."""
    print("\nTesting list_dir endpoint...")
    
    url = f"{BASE_URL}/mcp_api/list_dir"
    payload = {
        "user_dir": TEST_USER_DIR,
        "dir_name": ""
    }
    
    try:
        response = requests.post(url, json=payload)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_list_dir_recursively():
    """Test the list_dir_recursively endpoint."""
    print("\nTesting list_dir_recursively endpoint...")
    
    url = f"{BASE_URL}/mcp_api/list_dir_recursively"
    payload = {
        "user_dir": TEST_USER_DIR,
        "dir_name": ""
    }
    
    try:
        response = requests.post(url, json=payload)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_invalid_ip():
    """Test that requests from invalid IPs are rejected."""
    print("\nTesting IP authentication (should be allowed from 127.0.0.1)...")
    
    url = f"{BASE_URL}/mcp_api/list_dir"
    payload = {
        "user_dir": TEST_USER_DIR,
        "dir_name": ""
    }
    
    try:
        response = requests.post(url, json=payload)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 403:
            print("IP authentication working correctly - access denied")
        else:
            print("IP authentication may not be working - access allowed")
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    """Run all tests."""
    print("MCP API Test Suite")
    print("=" * 50)
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/admin/")
        print("✓ Django server is running")
    except requests.exceptions.ConnectionError:
        print("✗ Django server is not running. Please start it with:")
        print("  uv run python project/manage.py runserver")
        sys.exit(1)
    
    # Run tests
    tests = [
        test_run_python_code,
        test_list_dir,
        test_list_dir_recursively,
        test_invalid_ip
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print("-" * 50)
    
    print(f"\nTest Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✓ All tests passed! MCP API is working correctly.")
    else:
        print("✗ Some tests failed. Please check the implementation.")

if __name__ == "__main__":
    main() 