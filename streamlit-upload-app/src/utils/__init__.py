# FILE: /streamlit-upload-app/streamlit-upload-app/src/utils/__init__.py
# 该文件可以包含一些辅助函数，例如处理文件上传和发送HTTP请求的功能。

import requests

def upload_file(username: str, sessionname: str, file_path: str):
    url = f"http://your-backend-url/upload/{username}/{sessionname}"
    with open(file_path, 'rb') as file:
        files = {'files': file}
        response = requests.post(url, files=files)
    return response