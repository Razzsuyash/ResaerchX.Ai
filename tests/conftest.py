import os
from pathlib import Path

TEST_DB = Path("test_research.db")

os.environ.setdefault("OPENAI_API_KEY", "test-key")
os.environ.setdefault("TAVILY_API_KEY", "test-key")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-for-tests")
os.environ["DATABASE_URL"] = "sqlite:///./test_research.db"
os.environ["ALLOWED_ORIGINS"] = "http://localhost:8501"

if TEST_DB.exists():
    TEST_DB.unlink()


from backend.db.database import Base, engine
from backend.db import models  # noqa: F401

Base.metadata.create_all(bind=engine)
