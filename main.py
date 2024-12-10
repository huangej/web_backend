from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers.author import router as author_router

app = FastAPI()

# 啟用CORS
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

# 註冊 author 路由
app.include_router(author_router)
