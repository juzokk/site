from typing import Optional
from sqlmodel import SQLModel, Field


class teacher(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    surname: str
    email: str
    phone_number: str
    password: str
    average_rating: float | None = Field(default=5)

class student(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    surname: str
    email: str
    phone_number: str
    password: str

class advt(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    s_id: Optional[str] = Field(default=None)
    t_id: Optional[str] = Field(default=None)
    title: str
    sub: str
    desc: str