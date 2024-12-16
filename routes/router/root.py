
from fastapi import APIRouter, Depends, HTTPException, Request, File, UploadFile, Form
import os
from ..model.response import StandardResponse
from ..model.request import LoginRequest, RegisterRequest,ResetUserRequest
from datetime import datetime
from werkzeug.security import check_password_hash, generate_password_hash
from logger import logger
from typing import List
import requests
import dotenv

tts_url=dotenv.get("TTS_URL")

root_router = APIRouter(prefix="/root", tags=["root"])

allowed_extensions = [ ".pdf", ".docx", ".png",".jpg","jpeg"]
position="./upload_files"
UPLOAD_FILES_MAX_SIZE = eval( "10 * 1024 * 1024")  # 10MB

@root_router.get("/", tags=["root"])
async def root() -> StandardResponse:
    return StandardResponse(
        code=0,
        status="success",
        message="Welcome to Caizzzai api!",
    )


async def upload_files(files: List[UploadFile], position: str, username: str, session: str):

    urls=[]

    for file in files:
        _, ext = os.path.splitext(file.filename)
        ext = ext.lower()
        content = await file.read()

        if ext not in allowed_extensions:
            raise HTTPException(status_code=400, detail=f"不支持的文件类型: {file.filename}")

        if len(content) > UPLOAD_FILES_MAX_SIZE:
            raise HTTPException(status_code=413, detail=f"文件太大: {file.filename}")

        os.makedirs(f"{position}/{username}/{session}/", exist_ok=True)
        file_location = f"{position}/{username}/{session}/{file.filename}"

        urls.append(file_location)

        with open(file_location, "wb") as f:
            f.write(content)


    from podcastfy.client import generate_podcast
    transcript_file = generate_podcast(urls=["data/pdf/三国.pdf"],tts_model="edge",transcript_only=True,longform=False)

    transcript=os.read(transcript_file)

    return transcript


async def divide(transcript:str):
    import re

    person1_lines = []
    person2_lines = []

    matches = re.findall(r'<(Person1|Person2)>(.*?)</\1>', transcript, re.DOTALL)

    for match in matches:
        if match[0] == "Person1":
            person1_lines.append(match[1].strip())
        elif match[0] == "Person2":
            person2_lines.append(match[1].strip())

    return person1_lines,person2_lines
    


@root_router.post("/upload/{username}/{session}")
async def upload(username:str,session:str,files: List[UploadFile] = File(...)):


    transcript =await upload_files(files, username, session)

    person1_lines,person2_lines=await divide(transcript)

    person1_audio_list,person2_audio_list=[],[]



    headers = {"Content-Type": "application/json"}
    for i in range(len(person1_lines)):
        requestsdata = {
            "text": person1_lines[i],
            #"voice": "Person1",
            "request_id": "4000517517",
            "rank": 0
        }
        response = requests.post(tts_url, json=requestsdata, headers=headers)
        jsonresponse=response.json()
        person1_audio_list.append(jsonresponse['path'])

    




    

