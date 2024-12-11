from fastapi import APIRouter, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import os

router = APIRouter(tags=["file"])

# 使用基於 main.py 的路徑
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # 回到 web_backend 主目錄
static_dir = os.path.join(base_dir, "static")  # 指向正確的 static 資料夾

# 確保 static 資料夾存在
if not os.path.exists(static_dir):
    os.makedirs(static_dir)

@router.post("/uploadfile/")
async def create_upload_file(file: UploadFile):
    try:
        # 確保檔案有名稱
        if not file.filename:
            raise HTTPException(status_code=400, detail="File must have a name")

        # 儲存檔案的完整路徑
        file_path = os.path.join(static_dir, file.filename)
        print(f"Saving file to: {file_path}")  # 紀錄儲存路徑

        # 讀取檔案內容並儲存到指定路徑
        contents = await file.read()
        with open(file_path, "wb") as f:
            f.write(contents)

        # 返回成功訊息
        return JSONResponse(content={"filename": file.filename, "file_path": file_path})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error while saving file: {str(e)}")
