import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
INSTANCE_DIR = BASE_DIR / "instance"

INSTANCE_DIR.mkdir(parents=True, exist_ok=True)

load_dotenv(BASE_DIR / ".env")


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-key-change-before-deployment")

    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{(INSTANCE_DIR / 'attendance.db').as_posix()}"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False