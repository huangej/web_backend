import pymysql

def getDB():
    # 建立資料庫連線
    connection = pymysql.connect(
        host="localhost",
        user="root",
        password="12345678",
        database="final_web",
        charset="utf8mb4"
    )
    return connection
