
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
</Person2><Person1> "哦，我想最让人印象深刻的就是赵云如何单枪匹马冲出重围，救下阿斗。我甚至能想象那种紧迫感，还有他心里对主公和糜夫人的愧疚。”
</Person1><Person2> “确实，他为了保护阿斗付出了巨大的代价，而这么多文人墨客也为此留下诗篇赞美他的忠诚，这道出了‘忠臣’二字的不易。”
</Person2><Person1> “对了，看张飞在长坂桥上挺身而出，对抗整个曹军，那种气势简直可以用轰天震地来形容。他站在那里，以一敌百，用吼声震慑敌军！”
</Person1><Person2> “没错，那句‘我乃燕人张翼德也！谁敢与我决一死战？’真是经典之语。曹操为何会如此害怕张飞？这不仅是因为他的勇猛，还因为战略上的考虑吧。”
</Person2><Person1> “正是这样！曹操还特别提到要小心被诸葛孔明设计，所以即使没有埋伏，他们还是选择了退兵。”
</Person1><Person2> “这让我想到战争中的心理战，不仅要打实力上的优势，还得留有余地。而且这个时候刘备面临的也是一个生死攸关的局势，后有追兵前有大江，每一步都需要极其谨慎。”
</Person2><Person1> “你说得太对了，好似前有狼后有虎。那么当关云长出现之后，局势又发生怎样变化呢？”
</Person1><Person2> “关云长侍卫千里而来，一刀切割敌军如砍瓜切菜。这不只是打击敌军士气，更像是一线希望，将绝境中的刘备众人唤醒。今年居然还能联合反击！” 
</Person2><Person1> "可惜运筹帷幄之间，这三国间的纷争连绵不绝。最后曹操趁机调动兵马，如饿虎扑羊般细致周全，再次凑合两方力量，要怎么应对才好呢？” 
</Person1><Person2> "果然紧闭的大门可能因微风而开。在刘备最终决定投东吴之前，你怎么看孔明与鲁肃之间那番较量、合作？" 
</Person2><Person1> "这是智慧之源，它不仅体现了战术策略，也揭示了政权联结的重要性。孔明真的很聪明，他利用自己的资源去探知其他强者以促成联盟。" 
ικανός  ” 我们知道历史将继续推进，到底东吴会怎样应对这样的局势？期待下一次再给大家带来精彩分析！感谢大家收听这一期的PODCASTIFY！”  结束语，“再见各位，记得关注我们哦！” .</Person1>'''


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
            raise HTTPException(status_code=400, detail=f"不支持的文件类型: {file.filename}")

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
                raise HTTPException(status_code=404, detail="User not found")

            ses = conn.query(SessionSchema).filter(sessionname == sessionname).first()
            if ses:
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
        raise HTTPException(status_code=500, detail="Error creating session")

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
                            content_1=str(tts_audio_url+jsonresponse2['path']),
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
        




    

