from sqlmodel import SQLModel,Field
from typing import Optional


class Book(SQLModel,table=True):
    id:Optional[int]=Field(default=None,primary_key=True)
    title:str
    description:str

class student(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    surname: str
    email: str
    phone_number: str
    discord_username: str


class teacher(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    surname: str
    email: str
    phone_number: str
    discord_username: str
    area_of_training: int
    average_rating: float


class teacher_comments(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    student_id: int | None = Field(default=None, foreign_key='student.id')
    teacher_id: int | None = Field(default=None, foreign_key='teacher.id')
    comment_rating: float
    comment_text: str


class areas(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    discipline: str

class teacherarealink(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    teacher_id: int | None = Field(default=None, foreign_key='teacher.id')
    area_id: int | None = Field(default=None, foreign_key='areas.id')