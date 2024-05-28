from typing import Optional
from sqlmodel import SQLModel, Field


class teacher(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    surname: str
    email: str
    phone_number: str
    discord_username: str
    area_of_training: int
    average_rating: float

class student(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    surname: str
    email: str
    phone_number: str
    password: str

