# tests/test_config.py
import os
from unittest.mock import patch

from src.config import Config


def test_config_default_values():
    """Test config default values"""
    with patch.dict(os.environ, {"SECRET_KEY": "test_secret", "DATABASE_URL": "sqlite:///test.db"}):
        config = Config()
        assert config.ALGORITHM == "HS256"
        assert config.ACCESS_TOKEN_EXPIRE_MINUTES == 30
        assert config.SECRET_KEY == "test_secret"
        assert config.DATABASE_URL == "sqlite:///test.db"

