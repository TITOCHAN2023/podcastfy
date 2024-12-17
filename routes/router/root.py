
import json
from fastapi import APIRouter, Depends, HTTPException, Request, File, UploadFile, Form
from fastapi.responses import StreamingResponse

from sqlalchemy import or_

from middleware.mysql.models.conversation import ConversationSchema
from middleware.mysql.models.session import SessionSchema
from middleware.mysql.models.users import UserSchema
from middleware.mysql import session
import os
from ..model.response import StandardResponse
from datetime import datetime
from logger import logger
from typing import List
import requests
import dotenv

dotenv.load_dotenv()
tts_url = os.getenv("TTS_URL")
tts_audio_url = os.getenv("TTS_AUDIO_URL")
gemini_api_key = os.getenv("GEMINI_API_KEY")
openai_api_key = os.getenv("OPENAI_API_KEY")
base_url = os.getenv("BASE_URL")
test_text='''<Person1> "欢迎收听PODCASTIFY—你的个人生成AI播客！今天，我们将深入讨论《三国演义》中第四十二回的内容，主题是张翼德大闹长坂桥和刘豫州败走汉津口。这一段真的是跌宕起伏，精彩绝伦啊！”
</Person1><Person2> "完全同意！这一章中的战斗场面揭示了英雄们在困境中逆袭的光辉时刻。你觉得最吸引人的部分是什么呢？”
</Person2>'''

root_router = APIRouter(prefix="/root", tags=["root"])

allowed_extensions = [ ".pdf", ".docx", ".png",".jpg","jpeg"]
position="./upload_files"
UPLOAD_FILES_MAX_SIZE = eval( "10 * 1024 * 1024")  # 10MB

@root_router.get("/", tags=["root"])
async def root() -> StandardResponse:
    return StandardResponse(
        code=200,
        status="success",
        message="Welcome to Caizzzapi!",
    )


async def upload_files(files: List[UploadFile], username: str, sessionname: str):

    urls=[]

    for file in files:
        _, ext = os.path.splitext(file.filename)
        ext = ext.lower()
        content = await file.read()

        if ext not in allowed_extensions:
            raise HTTPException(status_code=400, detail=f"不支持的文件类型: {file.filename}:{ext}")

        if len(content) > UPLOAD_FILES_MAX_SIZE:
            raise HTTPException(status_code=413, detail=f"文件太大: {file.filename}")

        os.makedirs(f"{position}/{username}/{sessionname}/", exist_ok=True)
        file_location = f"{position}/{username}/{sessionname}/{file.filename}"

        urls.append(file_location)

        with open(file_location, "wb") as f:
            f.write(content)


    from podcastfy.client import generate_podcast

    transcript_file = generate_podcast(
        urls=urls,
        tts_model="edge",
        llm_model_name="gpt-4o-mini",
        api_key_label=openai_api_key,
        base_url=base_url,
        transcript_only=True,
        longform=False
        )

    with open(transcript_file, "r") as f:
        transcript = f.read()

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
    


@root_router.post("/upload/{username}/{sessionname}")
async def upload(username:str,sessionname:str,files: List[UploadFile] = File(...)):

    try:
        with session() as conn:
            user = conn.query(UserSchema).filter(UserSchema.username == username).first()
            if not user:
                logger.error(f"User not found: {username}")
                raise HTTPException(status_code=404, detail="User not found")

            logger.info(f"User found: {user.username}")

            ses = conn.query(SessionSchema)\
            .filter(SessionSchema.sessionname == sessionname)\
            .filter(SessionSchema.uid== user.uid)\
            .first()

            if ses:
                logger.error(f"Session already exists: {sessionname}")
                raise HTTPException(status_code=409, detail="Session already exists")

            ses = SessionSchema(
                uid=user.uid,
                sessionname=sessionname,
                create_at=datetime.now()
            )

            conn.add(ses)
            conn.commit()
            sid = ses.sid
            logger.info(f"Session created with ID: {sid}")

    except Exception as e:

        logger.error(f"Error creating session: {str(e)}")


    #transcript =await upload_files(files, username, sessionname)
    transcript = test_text

    logger.info(f"transcript: {transcript}")

    person1_lines,person2_lines=await divide(transcript)

    zipped_list = list(zip(person1_lines, person2_lines))

    logger.info(f"zipped_list: {zipped_list}")


    headers = {"Content-Type": "application/json"}
    async def generate():
        for i in zipped_list:

            try:    #交谈话语
                requestsdata = {
                    "text": i[0],
                    #"voice": "Person1",
                    "request_id": "4000517517",
                    "rank": 0
                }
                response = requests.post(tts_url, json=requestsdata, headers=headers)
                jsonresponse1=response.json()
                logger.info(f"jsonresponse1: {tts_audio_url}{jsonresponse1['path']}")
                yield f"data: {json.dumps({'audio_person_1': tts_audio_url+jsonresponse1['path']})}\n\n"

                requestsdata = {
                    "text": i[1],
                    #"voice": "Person2",
                    "request_id": "4000517517",
                    "rank": 0
                }
                response = requests.post(tts_url, json=requestsdata, headers=headers)
                jsonresponse2=response.json()
                logger.info(f"jsonresponse2: {tts_audio_url}{jsonresponse2['path']}")
                yield f"data: {json.dumps({'audio_person_2': tts_audio_url+jsonresponse2['path']})}\n\n"
                

                logger.info(f"Conversation added with SID: {sid}")

                with session() as conn:
                    conversation = ConversationSchema(
                            sid=sid,
                            content_1=str(tts_audio_url+jsonresponse1['path']),
                            content_2=str(tts_audio_url+jsonresponse2['path'])
                        )
                    conn.add(conversation)
                    conn.commit()
            except Exception as e:
                logger.error(f"audio[{i}] generation failed")
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
                continue
        yield f"data: [DONE]\n\n"
        
    



    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )
        




    

