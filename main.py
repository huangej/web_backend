from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .routers.author import router as author_router
from .routers.idol import router as idol_router 
from .routers.post import router as post_router 
from .routers.uploadFile import router as upload_router
import os

app = FastAPI()

# 使用基於 main.py 的路徑
base_dir = os.path.dirname(os.path.abspath(__file__))  # web_backend
static_dir = os.path.join(base_dir, "static")  # 指向正確的 static 資料夾

# 掛載 static 資料夾
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# 啟用 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允許所有來源
    allow_credentials=True,
    allow_methods=["*"],  # 允許所有 HTTP 方法
    allow_headers=["*"],  # 允許所有標頭
)

@app.get("/")
async def root():
    return {"message": "Hello World"}

# 註冊路由
app.include_router(author_router)
app.include_router(idol_router)
app.include_router(post_router)
app.include_router(upload_router)
