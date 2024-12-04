from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from .db import getDB

router = APIRouter(prefix="/author", tags=["author_api"])

# 定義使用者登入註冊
class AuthorRegister(BaseModel):
    author_account: str
    author_name: str
    author_password: str

class AuthorLogin(BaseModel):
    author_account: str
    author_password: str

#註冊
@router.post("/register")
async def register(author: AuthorRegister):
    db = getDB()
    cursor = db.cursor()

    try:
        # 檢查帳號是否已存在
        cursor.execute("SELECT * FROM author WHERE author_account = %s", (author.author_account,))
        existing_author = cursor.fetchone()
        if existing_author:
            raise HTTPException(status_code=400, detail="Account already exists")

        # 插入資料（直接存密碼）
        cursor.execute(
            "INSERT INTO author (author_account, author_name, author_password) VALUES (%s, %s, %s)",
            (author.author_account, author.author_name, author.author_password)
        )
        db.commit()
        return {"message": "Registration successful"}
    finally:
        cursor.close()
        db.close()


# 登入
@router.post("/login")
async def login(author: AuthorLogin):
    db = getDB()
    cursor = db.cursor()  

    try:
        # 查詢使用者帳號
        cursor.execute("SELECT * FROM author WHERE author_account = %s", (author.author_account,))
        existing_author = cursor.fetchone()  

        if not existing_author:
            raise HTTPException(status_code=400, detail="Invalid account or password")

        if author.author_password != existing_author[2]:
            raise HTTPException(status_code=400, detail="Invalid account or password")

        return {"message": "Login successful"}
    finally:
        cursor.close()
        db.close()

