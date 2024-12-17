# 文件内容：/streamlit-upload-app/streamlit-upload-app/README.md

# Streamlit 文件上传应用

该项目是一个使用 Streamlit 创建的简单文件上传应用程序。用户可以通过该应用程序上传文件，并将文件通过 POST 请求发送到后端 API。

## 项目结构

```
streamlit-upload-app
├── src
│   ├── app.py          # 应用程序的入口文件
│   └── utils
│       └── __init__.py # 辅助函数
├── requirements.txt     # 项目所需的 Python 库
└── README.md            # 项目文档
```

## 安装依赖

在项目根目录下运行以下命令以安装所需的依赖：

```
pip install -r requirements.txt
```

## 运行应用程序

在项目根目录下，使用以下命令启动 Streamlit 应用程序：

```
streamlit run src/app.py
```

## 使用方法

1. 打开浏览器并访问 `http://localhost:8501`。
2. 使用界面中的文件上传功能选择要上传的文件。
3. 点击上传按钮，将文件发送到后端 API。

## 贡献

欢迎任何形式的贡献！请提交问题或拉取请求。