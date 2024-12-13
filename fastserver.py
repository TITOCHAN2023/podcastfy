from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Welcome to Podcastfy"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}


'''upload file to vdb'''
@app.post("/{username}/uploadfile")
async def upload_file(vdbname: str,
    embedding_model: str = Form(...),
    base_url: str = Form(...),
    api_key: str = Form(...),file: UploadFile = File(...), info: Tuple[int, int] = Depends(jwt_auth)) -> StandardResponse:
    uid, _ = info

    

    _, ext = os.path.splitext(file.filename)
    ext = ext.lower()
    content = await file.read()

    is_admin = False
    with session() as conn:
        user = conn.query(UserSchema).filter(UserSchema.uid == uid).first()
        is_admin = user.is_admin

        if not conn.is_active:
            conn.rollback()
            conn.close()
        else:
            conn.commit()

        vdb = conn.query(VectorDBSchema).filter(VectorDBSchema.name == vdbname).first()
        if not vdb:
            raise HTTPException(status_code=404, detail="VectorDB not found")

        if not conn.is_active:
            conn.rollback()
            conn.close()
        else:
            conn.commit()

    if vdbname in public_vdb_list and not is_admin:
        raise HTTPException(status_code=400, detail="公共知识库不支持非管理员上传文件")

    if ext not in allowed_extensions:
        raise HTTPException(status_code=400, detail="不支持的文件类型")

    if len(content) > UPLOAD_FILES_MAX_SIZE:
        raise HTTPException(status_code=413, detail="文件太大")
    
    os.makedirs(f"{FAISS_INDEX_PATH}/{UPLOAD_FOLDER}/{str(uid)}/{hash_vdbname}", exist_ok=True)
    file_location = f"{FAISS_INDEX_PATH}/{UPLOAD_FOLDER}/{str(uid)}/{hash_vdbname}/{filename}{ext}"

    with open(file_location, "wb") as f:
        f.write(content)


    return StandardResponse(code=0, status="success", data={"info": f"文件'{file.filename}'成功存入'{vdbname}'知识库中"})
