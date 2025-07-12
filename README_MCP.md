# For Internal Use only

## Features 

- There will be a special allowed IP for example 127.0.0.1 as of now, as I am developing
- This IP can send following requests
    - mcp_api/run_python_code
    - mcp_api/list_dir
    - mcp_api/list_dir_recursively

- run_python_code
    -The payload for run_python_code contains following data
        - User dir name (the dir allocated to user in the master_dir)
        - A python code
    -Run this python code in the user's directory
    -Return the output / errors in Json format

- list_dir
    - The payload for list_dir contains following data
        - User Dir name
        - Dir name to be listed (may be empty, then means root directory of that user)
    - Return the list of dir  and files as paths rooted at users directory

- list_dir_recursively
    - User Dir name
    - The payload for list_dir contains following data
        - Dir name (may be empty, then means root directory of that user)
    - Return the list of dir  and files as paths rooted at users directory
    

# Implementation

- No need to create new models. etc., just create a new app mcp_api, and entertain the requests