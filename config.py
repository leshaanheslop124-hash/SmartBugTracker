import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    DB_SERVER = os.getenv("DB_SERVER")
    DB_NAME = os.getenv("DB_NAME")
    DB_DRIVER = os.getenv("DB_DRIVER")

    SQLALCHEMY_DATABASE_URI = (
        f"mssql+pyodbc://@{DB_SERVER}/{DB_NAME}"
        f"?driver={DB_DRIVER.replace(' ', '+')}"
        "&trusted_connection=yes"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False