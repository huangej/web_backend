from fastapi import FastAPI
from .routers.author import router as author_routor

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}

app.include_router(author_routor)