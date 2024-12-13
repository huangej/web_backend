import pymysql

def getDB():
    # 建立資料庫連線
    connection = pymysql.connect(
        host="localhost",
        user="root",
        password="han20000914",
        database="final_web"
    )
    return connection
