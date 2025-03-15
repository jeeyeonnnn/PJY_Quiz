import os

from dotenv import load_dotenv

load_dotenv("./app/config/pro.env")

class Setting:

    # DB 설정
    DB_USER = os.environ.get("DB_USER")
    DB_PW = os.environ.get("DB_PW")
    DB_PORT = os.environ.get("DB_PORT")
    DB_HOST = os.environ.get("DB_HOST")
    DB_NAME = os.environ.get("DB_NAME")

    # JWT 설정
    JWT_SECRET = os.environ.get("JWT_SECRET")
    JWT_ALGORITHM = os.environ.get("JWT_ALGORITHM")

    @property
    def get_db_url(self):
        return f'postgresql+asyncpg://{self.DB_USER}:{self.DB_PW}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}'

setting = Setting()