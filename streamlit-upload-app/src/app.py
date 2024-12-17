import streamlit as st
import requests
import json
import dotenv
import os

dotenv.load_dotenv()
url=os.getenv("URL")
# 设置页面标题
st.title("文件上传应用")

# 创建文件上传组件
uploaded_file = st.file_uploader("选择一个文件", type=["txt", "csv", "xlsx", "pdf", "docx"])

# 输入用户名和会话名称
username = st.text_input("用户名")
sessionname = st.text_input("会话名称")

# 上传文件的按钮
if st.button("上传文件"):
    if uploaded_file is not None and username and sessionname:
        # 发送POST请求到后端API
        files = {'files': uploaded_file}

        response = requests.post(f"http://{url}/root/upload/{username}/{sessionname}", files=files, stream=True)

        if response.status_code == 200:
            for line in response.iter_lines():
                if line:
                    decoded_line = line.decode('utf-8')

                    if decoded_line.startswith('data: '):
                        decoded_line = decoded_line[len('data: '):]
                    if decoded_line.strip() == '[DONE]':
                        break
                    try:
                        data = json.loads(decoded_line)
                        if 'audio_person_1' in data:
                            st.markdown(f"## person 1:")
                            st.markdown(data['text_person_1'])
                            st.audio(data['audio_person_1'])
                        if 'audio_person_2' in data:
                            st.markdown(f"## person 2:")
                            st.markdown(data['text_person_2'])
                            st.audio(data['audio_person_2'])

                    except json.JSONDecodeError as e:
                        continue
    else:
        st.error("请确保选择文件并填写用户名和会话名称。")