from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from .db import getDB

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

# 新增偶像團體
@router.post("/create")
async def create_idol(idol: IdolCreate):
    db = getDB()
    cursor = db.cursor()

    try:
        cursor.execute(
            "INSERT INTO idol (group_name, start_time, group_company) VALUES (%s, %s, %s)",
            (idol.group_name, idol.start_time, idol.group_company)
        )
        db.commit()
        return {"message": "Idol created successfully"}
    finally:
        cursor.close()
        db.close()

# 取得所有偶像(這個是測試方便用，應該不會用到這個)
@router.get("/")
async def get_idols():
    db = getDB()
    cursor = db.cursor()

    try:
        cursor.execute("SELECT group_id, group_name, start_time, group_company FROM idol")
        idols = cursor.fetchall()
        return [{"group_id": i[0], "group_name": i[1], "group_pic": i[2],} for i in idols]
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

# 修改偶像資料
@router.put("/{group_id}")
async def update_idol(group_id: int, idol: IdolUpdate):
    db = getDB()
    cursor = db.cursor()

    try:
        update_fields = []
        values = []
        if idol.group_name:
            update_fields.append("group_name = %s")
            values.append(idol.group_name)
        if idol.start_time:
            update_fields.append("start_time = %s")
            values.append(idol.start_time)
        if idol.group_company:
            update_fields.append("group_company = %s")
            values.append(idol.group_company)

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
