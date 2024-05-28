from fastapi import FastAPI, Form, status, HTTPException, Depends, Request, Response
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from models import *
from database import engine
from sqlmodel import Session, select
from typing import Annotated

app = FastAPI(
    description='repetitor'
)

templates = Jinja2Templates('templates')

session = Session(bind=engine)


@app.get('/', response_model=teacher, tags=['Pages'])
async def get_all_teacher(request: Request):
    statement = select(teacher)
    result = session.exec(statement).all()

    if result == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return templates.TemplateResponse(
        request=request,
        name='index.html',
        context={
            'result': result
        }
    )


@app.get('/teacher/{teacher_id}', response_model=teacher, tags=['Pages'])
async def get_a_teacher(request: Request, teacher_id: int):
    statement = select(teacher).where(teacher.id == teacher_id)
    result = session.exec(statement).first()

    if result == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return templates.TemplateResponse(
        request=request,
        name='teacher_card.html',
        context={
            'id': result.id,
            'name': result.name,
            'surname': result.surname,
            'email': result.email,
            'phone_number': result.phone_number,
            'discord_username': result.discord_username,
            'area_of_training': result.area_of_training,
            'average_rating': result.average_rating
        }
    )


@app.get('/login', tags=['Pages'])
async def get_login_page(request: Request):
    cookie = request.cookies.get('id')

    if cookie != None:
        return RedirectResponse('/profile/' + cookie, status_code=302)

    return templates.TemplateResponse('login.html', {'request': request})


@app.get('/registration', tags=['Pages'])
async def get_registration_page(request: Request):
    return templates.TemplateResponse('registration.html', {'request': request})


@app.get('/profile/{student_id}', response_model=student, tags=['Pages'])
async def get_profile(request: Request, student_id: int):
    statement = select(student).where(student.id == student_id)
    result = session.exec(statement).first()

    if result == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return templates.TemplateResponse(
        request=request,
        name='profile.html',
        context={
            'id': result.id,
            'name': result.name,
            'surname': result.surname,
            'email': result.email,
            'phone_number': result.phone_number,
            'password': result.password
        }
    )

@app.post('/teacher', response_model=teacher, status_code=status.HTTP_201_CREATED)
async def create_a_teacher(teach: Annotated[teacher, Depends()]):
    new_teach = teacher(id = teach.id, name=teach.name, surname=teach.surname, email=teach.email, phone_number=teach.phone_number, discord_username=teach.discord_username, area_of_training=teach.area_of_training, average_rating=teach.average_rating)

    session.add(new_teach)

    session.commit()

    return new_teach


@app.post('/registration', status_code=status.HTTP_201_CREATED,
          response_class=RedirectResponse, tags=['Account'])
async def create_a_student(name: str = Form(...),
                            surname: str = Form(...),
                            email: str = Form(...),
                            phone_number: str = Form(...),
                            password: str = Form(...),
                            remember: Optional[bool] = Form(default=False)) -> RedirectResponse:
    statement = select(student).where(student.email == email or student.phone_number == phone_number)
    result = session.exec(statement).one_or_none()

    new_student = student(name=name, surname=surname,
                        email=email, phone_number=phone_number, password=password)

    if result == None:
        session.add(new_student)
        session.commit()

        response = RedirectResponse('/profile/' + str(new_student.id), status_code=302)
        if remember == True:
            response.set_cookie(key="id", value=str(new_student.id), max_age=15695000)
        return response

    return RedirectResponse('/registration', status_code=302)


@app.post('/login', response_class=RedirectResponse, tags=['Account'])
async def get_student(email_login: str = Form(...),
                   password_login: str = Form(...),
                   remember: Optional[bool] = Form(default=False)) -> RedirectResponse:
    email_statement = select(student).where(student.email == email_login)
    email_result = session.exec(email_statement).first()

    password_statement = select(student).where(student.password == password_login)
    password_result = session.exec(password_statement).first()

    if email_result != None:
        if email_result.id == password_result.id:
            response = RedirectResponse('/profile/' + str(email_result.id), status_code=302)
            if remember == True:
                response.set_cookie(key="id", value=str(email_result.id), max_age=15695000)
            return response


@app.get('/profile', tags=['Account'])
async def switch_account(response: Response):
    response = RedirectResponse('/login', status_code=302)
    response.delete_cookie('id')
    return response
