from backend.db.database import Base, engine
from backend.db import models  # noqa: F401


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
