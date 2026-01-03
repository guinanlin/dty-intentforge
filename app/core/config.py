"""配置管理"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings:
    """应用配置"""
    MODEL_PATH: str = str(BASE_DIR / "models" / "latest_nlu.tar.gz")
    API_PORT: int = int(os.getenv("API_PORT", "8200"))


settings = Settings()
