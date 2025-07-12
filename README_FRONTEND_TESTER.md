# MCP API Frontend Tester

A lightweight, single HTML file for manually testing the MCP API endpoints.

## Features

- **Single File**: Everything is contained in one HTML file (CSS and JavaScript embedded)
- **Three Tabs**: Test all three MCP API endpoints
  - Run Python Code
  - List Directory
  - List Directory Recursively
- **Modern UI**: Clean, responsive design with gradient backgrounds
- **Real-time Testing**: Instant feedback with JSON responses
- **Configuration**: Easy to change base URL and user directory
- **Examples**: Built-in example code for Python execution
- **Keyboard Shortcuts**: Ctrl+Enter to execute current tab's function

## How to Use

### 1. Start the Django Server

```bash
# Activate virtual environment
./.venv/Scripts/Activate

# Start the server
uv run python project/manage.py runserver
```

### 2. Open the Tester

Simply open `mcp_api_tester.html` in your web browser. You can:
- Double-click the file
- Drag and drop into browser
- Open via browser's File menu

### 3. Configure Settings

At the top of the page, you can configure:
- **Base URL**: Default is `http://127.0.0.1:8000`
- **User Directory**: Default is `test_user`

### 4. Test the Endpoints

#### Run Python Code Tab
- Enter Python code in the textarea
- Click "Execute Code" or press Ctrl+Enter
- View the execution results

#### List Directory Tab
- Optionally enter a subdirectory name
- Click "List Directory" or press Ctrl+Enter
- View directory contents

#### List Recursive Tab
- Optionally enter a subdirectory name
- Click "List Recursively" or press Ctrl+Enter
- View recursive directory listing

## Features

### Configuration Persistence
- Settings are automatically saved to localStorage
- Your configuration will be remembered between sessions

### Example Code
- Click "Load Example" to get sample Python code
- Multiple examples are available and randomly selected

### Response Display
- **Green**: Successful responses
- **Red**: Error responses
- **Formatted JSON**: Easy to read response format
- **Scrollable**: Long responses are scrollable

### Keyboard Shortcuts
- **Ctrl+Enter**: Execute the current tab's function
- **Tab**: Navigate between form fields

## Troubleshooting

### Common Issues

1. **Connection Error**
   - Make sure Django server is running
   - Check the base URL in configuration
   - Verify the server is accessible

2. **403 Forbidden**
   - Check if your IP is in the allowed list (default: 127.0.0.1)
   - Verify the MCP middleware is working

3. **404 Not Found**
   - Ensure the MCP API URLs are properly configured
   - Check if the Django server is running on the correct port

4. **User Directory Not Found**
   - Create the user directory in `project/master_dir/`
   - Example: `mkdir project/master_dir/test_user`

### Testing Different Scenarios

1. **Test with non-existent user directory**
   - Change user directory to something that doesn't exist
   - Should get an error response

2. **Test with invalid Python code**
   - Enter syntax error in Python code
   - Should get error output in response

3. **Test with empty directory**
   - Use a user directory with no files
   - Should get empty items list

## File Structure

```
BACKEND/
├── mcp_api_tester.html          # Frontend tester (this file)
├── README_FRONTEND_TESTER.md    # This documentation
├── project/
│   ├── mcp_api/                 # MCP API backend
│   └── master_dir/
│       └── test_user/           # Test user directory
└── ...
```

## Browser Compatibility

- **Chrome**: Full support
- **Firefox**: Full support
- **Safari**: Full support
- **Edge**: Full support
- **Mobile browsers**: Responsive design supported

## Security Notes

- This tester is for development use only
- It connects to localhost by default
- IP authentication is handled by the backend
- No sensitive data is stored in the frontend

## Customization

You can easily customize the tester by editing the HTML file:

- **Colors**: Modify CSS variables in the `<style>` section
- **Examples**: Add more Python code examples in the JavaScript
- **Endpoints**: Update API endpoints if they change
- **UI**: Modify the layout and styling as needed 