from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

import app.db.models  # Ensure models are registered with Base.metadata
