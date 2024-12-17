import streamlit as st
import requests
import json

# 设置页面标题
st.title("文件上传应用")

# 创建文件上传组件
uploaded_file = st.file_uploader("选择一个文件", type=["txt", "csv", "xlsx","pdf","docx"])

# 输入用户名和会话名称
username = st.text_input("用户名")
sessionname = st.text_input("会话名称")

# 上传文件的按钮
if st.button("上传文件"):
    if uploaded_file is not None and username and sessionname:
        # 发送POST请求到后端API
        files = {'files': uploaded_file.getvalue()}
        response = requests.post(f"http://183.131.7.9:8172/root/upload/{username}/{sessionname}", files=files)

        # 处理响应
        if response.status_code == 200:
            st.success("文件上传成功！")
            # 假设后端返回的数据格式为多条 {"audio_person_1": "audio_url"} 和 {"audio_person_2": "audio_url"}
            data = response.json()
            person1_lines = []
            person2_lines = []

            for item in data:
                if "audio_person_1" in item:
                    person1_lines.append(item["audio_person_1"])
                elif "audio_person_2" in item:
                    person2_lines.append(item["audio_person_2"])

            # 显示Person1和Person2的会话
            st.header("会话记录")
            for p1, p2 in zip(person1_lines, person2_lines):
                st.subheader("Person1:")
                st.audio(p1)
                st.subheader("Person2:")
                st.audio(p2)
        else:
            st.error(f"文件上传失败: {response.text}")
    else:
        st.error("请确保选择文件并填写用户名和会话名称。")