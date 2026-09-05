from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


# Import models to ensure they are registered with Base.metadata
