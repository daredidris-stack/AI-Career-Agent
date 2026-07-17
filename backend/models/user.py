from sqlalchemy import Column, Integer, String, DateTime

from backend.core.time import utc_now
from backend.database.database import Base


class User(Base):

    __tablename__ = "users"


    id = Column(
        Integer,
        primary_key=True,
        index=True
    )


    email = Column(
        String,
        unique=True,
        index=True,
        nullable=False
    )


    password_hash = Column(
        String,
        nullable=False
    )


    first_name = Column(
        String,
        nullable=True
    )


    last_name = Column(
        String,
        nullable=True
    )


    created_at = Column(
        DateTime,
        default=utc_now
    )
