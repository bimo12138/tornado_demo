from sqlalchemy import create_engine # 创建引擎对象的模块
from sqlalchemy.ext.declarative import declarative_base # 基础类模块
from sqlalchemy.orm import sessionmaker # 创建和数据库连接会话

HOST = "127.0.0.1"
# MySQL 默认是3306端口
PORT = "3306"
DATABASE = "tornado_server"
USERNAME = "bimo"
PASSWORD = "qwe123"
# 需要安装 pymysql
DB_URL = "mysql+pymysql://{}:{}@{}:{}/{}?charset=utf8".format(USERNAME, PASSWORD, HOST, PORT, DATABASE)

engine = create_engine(DB_URL)
dbSession = sessionmaker(bind=engine)
session = dbSession()
Base = declarative_base(engine)
