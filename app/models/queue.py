from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime
from sqlmodel import Field, SQLModel


class Queue(SQLModel, table=True):
    __tablename__ = "queue"

    id: int = Field(default=None, primary_key=True)
    name: str = Field(..., description="Queue name (process key)")
    description: str = Field(..., description="Description of the queue")
    is_active: bool = Field(sa_column=Column(Boolean, default=True))
    created_at: datetime = Field(
        default_factory=datetime.utcnow, sa_column=Column(DateTime(timezone=True), nullable=False)
    )
