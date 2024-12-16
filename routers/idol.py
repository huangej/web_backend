from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from .db import getDB
from fastapi import UploadFile, File, Form
from fastapi.responses import FileResponse
import os
router = APIRouter(prefix="/idol", tags=["idol_api"])

# 定義偶像資料
class IdolCreate(BaseModel):
    group_name: str
    start_time: str
    group_company: str

class IdolUpdate(BaseModel):
    group_name: str = None
    start_time: str = None
    group_company: str = None

# 設定 static 資料夾的路徑
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
static_dir = os.path.join(base_dir, "static")
if not os.path.exists(static_dir):
    os.makedirs(static_dir)

def save_image(file: UploadFile) -> str:
    if not file.filename:
        raise HTTPException(status_code=400, detail="File must have a name")
    relative_path = f"static/{file.filename}"
    absolute_path = os.path.join(static_dir, file.filename)
    with open(absolute_path, "wb") as pic_file:
        pic_file.write(file.file.read())
    return relative_path

@router.get("/image/{filename}")
async def get_image(filename: str):
    file_path = os.path.join(static_dir, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Image not found")
    return FileResponse(file_path)



# 新增偶像團體
@router.post("/create")
async def create_idol(
    group_name: str = Form(...),
    start_time: str = Form(...),
    group_company: str = Form(...),
    group_pic: UploadFile = File(None)  # 圖片文件為可選
):
    db = getDB()
    cursor = db.cursor()

    try:
        pic_path = None
        if group_pic:
            pic_path = save_image(group_pic)  # 保存圖片並獲取相對路徑

        cursor.execute(
            "INSERT INTO idol (group_name, start_time, group_company, group_pic) VALUES (%s, %s, %s, %s)",
            (group_name, start_time, group_company, pic_path)
        )
        db.commit()
        return {"message": "Idol created successfully"}
    finally:
        cursor.close()
        db.close()

#取得所有偶像團體 (只返回需要的 group_id 和 group_name)
@router.get("/")
async def get_idols():
    db = getDB()
    cursor = db.cursor()

    try:
        cursor.execute("SELECT group_id, group_name, start_time, group_company, group_pic FROM idol")
        idols = cursor.fetchall()
        return [{"group_id": i[0], "group_name": i[1],"start_time": i[2], "group_company": i[3], "group_pic": i[4], } for i in idols]
    finally:
        cursor.close()
        db.close()


# 取得單一偶像的詳細資訊
@router.get("/{group_id}")
async def get_idol_by_id(group_id: int):
    db = getDB()
    cursor = db.cursor()

    try:
        cursor.execute(
            "SELECT group_id, group_name, start_time, group_company FROM idol WHERE group_id = %s",
            (group_id,)
        )
        idol = cursor.fetchone()
        if not idol:
            raise HTTPException(status_code=404, detail="Idol not found")
        return {
            "group_id": idol[0],
            "group_name": idol[1],
            "start_time": idol[2],
            "group_company": idol[3]
        }
    finally:
        cursor.close()
        db.close()

# 修改
@router.put("/{group_id}")
async def update_idol(
    group_id: int,
    group_name: str = Form(None),
    start_time: str = Form(None),
    group_company: str = Form(None),
    group_pic: UploadFile = File(None)
):
    db = getDB()
    cursor = db.cursor()

    try:
        update_fields = []
        values = []

        if group_name:
            update_fields.append("group_name = %s")
            values.append(group_name)
        if start_time:
            update_fields.append("start_time = %s")
            values.append(start_time)
        if group_company:
            update_fields.append("group_company = %s")
            values.append(group_company)
        if group_pic:
            pic_path = save_image(group_pic)
            update_fields.append("group_pic = %s")
            values.append(pic_path)

        if not update_fields:
            raise HTTPException(status_code=400, detail="No fields to update")

        values.append(group_id)
        cursor.execute(f"UPDATE idol SET {', '.join(update_fields)} WHERE group_id = %s", tuple(values))
        db.commit()

        return {"message": "Idol updated successfully"}
    finally:
        cursor.close()
        db.close()

# 刪除偶像團體
@router.delete("/{group_id}")
async def delete_idol(group_id: int):
    db = getDB()
    cursor = db.cursor()

    try:
        cursor.execute("DELETE FROM idol WHERE group_id = %s", (group_id,))
        db.commit()
        return {"message": "Idol deleted successfully"}
    finally:
        cursor.close()
        db.close()
