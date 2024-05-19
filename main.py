from fastapi import FastAPI, status, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.exceptions import HTTPException
from models import *
from database import engine
from sqlmodel import Session,select
from typing import Optional, List, Annotated

app=FastAPI()

templates = Jinja2Templates('templates')

session=Session(bind=engine)


@app.get('/', response_model=List[Book], status_code=status.HTTP_200_OK)
async def get_all_book(request: Request):
    statement = select(Book)
    result = session.exec(statement).all()

    if result == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return templates.TemplateResponse(
        request = request,
        name = 'index.html',
        context = {
            'result': result
        }
    )

@app.post('/books', response_model=Book,
          status_code=status.HTTP_201_CREATED)
async def create_a_books(book:Book):
    new_book=Book(title=book.title,description=book.description)

    session.add(new_book)

    session.commit()

    return new_book

@app.get('/book/{book_id}', response_model=Book)
async def get_a_book(request: Request, book_id: int):
    statement = select(Book).where(Book.id == book_id)
    result = session.exec(statement).first()

    if result == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return templates.TemplateResponse(
        request = request,
        name = 'book_card.html',
        context = {
            'id': result.id,
            'title': result.title,
            'price': result.description
        }
    )



@app.put('/books/{book_id}')
async def get_all_books(book_id:int,book:Book):
    statement=select(Book).where(Book.id==book_id)

    result=session.exec(statement).first()

    result.title=book.title
    result.description=book.description

    session.commit()

    return result




@app.delete('/book/{book_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_a_book(book_id:int):
    statement = select(Book).where(Book.id==book_id)

    result = session.exec(statement).one_or_none()

    if result == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Resource Not Found")

    session.delete(result)

    return result

@app.get('/')
async def get_index_page(request: Request):
    return templates.TemplateResponse('index.html', {'request': request})

@app.get('/login')
async def get_login_page(request: Request):
    return templates.TemplateResponse('login.html', {'request': request})

@app.post('/student', response_model=student, status_code=status.HTTP_201_CREATED)
async def create_a_student(stud: Annotated[student, Depends()]):
    new_stud = student(id = stud.id, name=stud.name, surname=stud.surname, email=stud.email, phone_number=stud.phone_number, discord_username=stud.discord_username)

    session.add(new_stud)

    session.commit()

    return new_stud

@app.post('/teacher', response_model=teacher, status_code=status.HTTP_201_CREATED)
async def create_a_teacher(teach: Annotated[teacher, Depends()]):
    new_teach = teacher(id = teach.id, name=teach.name, surname=teach.surname, email=teach.email, phone_number=teach.phone_number, discord_username=teach.discord_username, area_of_training=teach.area_of_training, average_rating=teach.average_rating)

    session.add(new_teach)

    session.commit()

    return new_teach


