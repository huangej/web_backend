from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os
from .db import getDB

router = APIRouter(prefix="/post", tags=["post_api"])

# 設定 static 資料夾的正確路徑
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) 
static_dir = os.path.join(base_dir, "static")  
if not os.path.exists(static_dir):
    os.makedirs(static_dir)

# 儲存圖片的東西
def save_image(file: UploadFile) -> str:
    if not file.filename:
        raise HTTPException(status_code=400, detail="File must have a name")
    relative_path = f"static/{file.filename}" 
    absolute_path = os.path.join(static_dir, file.filename) 
    with open(absolute_path, "wb") as pic_file:
        content = file.file.read()
        pic_file.write(content)
    return relative_path  

class PostCreate(BaseModel):
    group_id: int
    author_account: str
    post_title: str
    post_content: str
    post_date: str

class PostUpdate(BaseModel):
    group_id: int = None
    post_title: str = None
    post_content: str = None
    post_date: str = None

    

# 新增 Post
@router.post("/create")
async def create_post(
    group_id: int = Form(...),
    author_account: str = Form(...),
    post_title: str = Form(...),
    post_content: str = Form(...),
    post_date: str = Form(...),
    post_pic: UploadFile = File(...)
):
    db = getDB()
    cursor = db.cursor()
    try:
        pic_path = save_image(post_pic)

        cursor.execute(
            "INSERT INTO post (group_id, author_account, post_title, post_content, post_date, post_pic) VALUES (%s, %s, %s, %s, %s, %s)",
            (group_id, author_account, post_title, post_content, post_date, pic_path),
        )
        db.commit()

        return {
            "message": "Post created successfully",
            "data": {
                "group_id": group_id,
                "author_account": author_account,
                "post_title": post_title,
                "post_content": post_content,
                "post_date": post_date,
                "post_pic_url": f"/{pic_path}" 
            }
        }
    finally:
        cursor.close()
        db.close()

# 取得所有 Post
@router.get("/")
async def get_posts():
    db = getDB()
    cursor = db.cursor()

    try:
        cursor.execute("SELECT p.post_id, p.group_id, i.group_name, p.author_account,  p.post_title,  p.post_content,  p.post_date,  p.post_pic FROM post p JOIN idol i ON p.group_id = i.group_id")
        posts = cursor.fetchall()
        return [
            {
                "post_id": p[0],
                "group_id": p[1],
                "group_name": p[2],
                "author_account": p[3],
                "post_title": p[4],
                "post_content": p[5],
                "post_date": p[6],
                "post_pic": p[7],  # 使用相對路徑
            }
            for p in posts
        ]
    finally:
        cursor.close()
        db.close()

# 取得單一 Post 的詳細資訊
@router.get("/{post_id}")
async def get_post_by_id(post_id: int):
    db = getDB()
    cursor = db.cursor()

    try:
        cursor.execute(
            "SELECT post_id, group_id, author_account, post_title, post_content, post_date, post_pic FROM post WHERE post_id = %s",
            (post_id,),
        )
        post = cursor.fetchone()
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")

        return {
            "post_id": post[0],
            "group_id": post[1],
            "author_account": post[2],
            "post_title": post[3],
            "post_content": post[4],
            "post_date": post[5],
            "post_pic_url": f"/{post[6]}" if post[6] else None,  
        }
    finally:
        cursor.close()
        db.close()

# 更新 Post
@router.put("/{post_id}")
async def update_post(
    post_id: int,
    post_title: str = Form(None),
    post_content: str = Form(None),
    post_date: str = Form(None),
    post_pic: UploadFile = File(None)
):
    db = getDB()
    cursor = db.cursor()

    try:
        pic_path = None
        if post_pic:
            pic_path = save_image(post_pic)

        update_fields = []
        values = []
        if post_title:
            update_fields.append("post_title = %s")
            values.append(post_title)
        if post_content:
            update_fields.append("post_content = %s")
            values.append(post_content)
        if post_date:
            update_fields.append("post_date = %s")
            values.append(post_date)
        if pic_path:
            update_fields.append("post_pic = %s")
            values.append(pic_path)

        if not update_fields:
            raise HTTPException(status_code=400, detail="No fields to update")

        values.append(post_id)
        cursor.execute(f"UPDATE post SET {', '.join(update_fields)} WHERE post_id = %s", tuple(values))
        db.commit()

        return {"message": "Post updated successfully"}
    finally:
        cursor.close()
        db.close()


# 刪除 Post
@router.delete("/{post_id}")
async def delete_post(post_id: int):
    db = getDB()
    cursor = db.cursor()

    try:
        cursor.execute("DELETE FROM post WHERE post_id = %s", (post_id,))
        db.commit()
        return {"message": "Post deleted successfully"}
    finally:
        cursor.close()
        db.close()

# 提供圖片檔案
@router.get("/image/{filename}")
async def get_image(filename: str):
    file_path = os.path.join(static_dir, filename)  
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Image not found")
    return FileResponse(file_path)


