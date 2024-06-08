import bcrypt
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

    s_cookie = request.cookies.get('student_id')
    t_cookie = request.cookies.get('teacher_id')

    flag = False

    if s_cookie != None or t_cookie != None:
        flag = True
    if t_cookie != None:
        return RedirectResponse('/teacher', status_code=302)
    statement = select(advt).where(advt.t_id != None)
    result = session.exec(statement).all()

    if result == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return templates.TemplateResponse(
        request=request,
        name='index.html',
        context={
            'result': result,
            'flag': flag
        }
    )
    
@app.get('/teacher', response_model=teacher, tags=['Pages'])
async def get_all_students(request: Request):
    statement = select(advt).where(advt.s_id != None)
    result = session.exec(statement).all()

    s_cookie = request.cookies.get('student_id')
    t_cookie = request.cookies.get('teacher_id')

    if s_cookie != None or t_cookie == None:
        return RedirectResponse('/', status_code=302)

    if result == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return templates.TemplateResponse(
        request=request,
        name='teacher.html',
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
            'average_rating': result.average_rating
        }
    )


@app.get('/login', tags=['Pages'])
async def get_login_page(request: Request):
    s_cookie = request.cookies.get('student_id')
    t_cookie = request.cookies.get('teacher_id')

    if s_cookie != None:
        return RedirectResponse('/profile/student/' + s_cookie, status_code=302)
    elif t_cookie != None:
        return RedirectResponse('/profile/teacher/' + t_cookie, status_code=302)

    return templates.TemplateResponse('login.html', {'request': request})


@app.get('/registration', tags=['Pages'])
async def get_registration_page(request: Request):
    return templates.TemplateResponse('registration.html', {'request': request,})

@app.get('/advt_card/{advt_id}', tags=['Pages'])
async def get_registration_page(request: Request, advt_id: int):
    
    statement = select(advt).where(advt.id == advt_id)
    result = session.exec(statement).first()
    
    t_statement = select(teacher).where(teacher.id == result.t_id)
    t_result = session.exec(t_statement).first()
    
    s_statement = select(student).where(student.id == result.s_id)
    s_result = session.exec(s_statement).first()
    
    return templates.TemplateResponse(
        request=request,
        name='advt_card.html',
        context={
            'title': result.title,
            'sub': result.sub,
            'desc': result.desc,
            's_result': s_result,
            't_result': t_result
        }
    )

@app.get('/advt', tags=['Pages'])
async def get_advt_page(request: Request):
    s_cookie = request.cookies.get('student_id')
    t_cookie = request.cookies.get('teacher_id')
    
    if s_cookie == None and t_cookie == None:
        return RedirectResponse('/login', status_code=302)

    return templates.TemplateResponse('advt.html', {'request': request})



@app.post('/advt', status_code=status.HTTP_201_CREATED,
          response_class=RedirectResponse)
async def create_advt(request: Request, title: str = Form(...),
                      sub: str = Form(...),
                      desc: str = Form(...)) -> RedirectResponse:
    s_cookie = request.cookies.get('student_id')
    t_cookie = request.cookies.get('teacher_id')
    new = advt(s_id = s_cookie, t_id = t_cookie, title = title, sub = sub, desc = desc)
    
    session.add(new)
    session.commit()

    return RedirectResponse('/advt_card/' + str(new.id), status_code=302)

@app.get('/profile/student/{student_id}', response_model=student, tags=['Pages'])
async def get_profile_student(request: Request, student_id: int):
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
    
@app.get('/profile/teacher/{teacher_id}', response_model=teacher, tags=['Pages'])
async def get_profile_teacher(request: Request, teacher_id: int):
    statement = select(teacher).where(teacher.id == teacher_id)
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


@app.post('/registration', status_code=status.HTTP_201_CREATED,
          response_class=RedirectResponse, tags=['Account'])
async def create_a_student(name: str = Form(...),
                           surname: str = Form(...),
                           email: str = Form(...),
                           phone_number: str = Form(...),
                           password: str = Form(...),
                           teacher_check: Optional[bool] = Form(default=False),
                           remember: Optional[bool] = Form(default=False)) -> RedirectResponse:
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    t_check = select(teacher).where(teacher.email == email and teacher.phone_number == phone_number)
    s_check = select(student).where(student.email == email and student.phone_number == phone_number)

    t_check_result = session.exec(t_check).first()
    s_check_result = session.exec(s_check).first()

    if t_check_result != None and s_check_result != None:
        return RedirectResponse('/registration', status_code=302)

    if teacher_check == True:
        new = teacher(name=name, surname=surname,
                      email=email, phone_number=phone_number, password=hashed_password)
        statement = select(teacher).where(teacher.email == email or teacher.phone_number == phone_number)
        result = session.exec(statement).one_or_none()

        if result == None:
            session.add(new)
            session.commit()

            response = RedirectResponse('/profile/teacher/' + str(new.id), status_code=302)
            response.delete_cookie('teacher_id')
            response.delete_cookie('student_id')

            if remember == True:
                response.set_cookie(key="teacher_id", value=str(new.id), max_age=15695000)
            return response
    else:
        statement = select(student).where(student.email == email or student.phone_number == phone_number)
        result = session.exec(statement).one_or_none()

        new = student(name=name, surname=surname,
                      email=email, phone_number=phone_number, password=hashed_password)

        if result == None:
            session.add(new)
            session.commit()

            response = RedirectResponse('/profile/student/' + str(new.id), status_code=302)
            response.delete_cookie('teacher_id')
            response.delete_cookie('student_id')
            if remember == True:
                response.set_cookie(key="student_id", value=str(new.id), max_age=15695000)
            return response

    return RedirectResponse('/registration', status_code=302)


@app.post('/login', response_class=RedirectResponse, tags=['Account'])
async def get_student(email_login: str = Form(...),
                      password_login: str = Form(...),
                      remember: Optional[bool] = Form(default=False)) -> RedirectResponse:
    email_statement = select(student).where(student.email == email_login)
    email_result = session.exec(email_statement).first()

    if email_result and bcrypt.checkpw(password_login.encode('utf-8'), email_result.password.encode('utf-8')):
        response = RedirectResponse('/profile/student/' + str(email_result.id), status_code=302)
        if remember:
            response.set_cookie(key="student_id", value=str(email_result.id), max_age=15695000)
        return response

    email_statement = select(teacher).where(teacher.email == email_login)
    email_result = session.exec(email_statement).first()

    if email_result and bcrypt.checkpw(password_login.encode('utf-8'), email_result.password.encode('utf-8')):
        response = RedirectResponse('/profile/teacher/' + str(email_result.id), status_code=302)
        if remember:
            response.set_cookie(key="teacher_id", value=str(email_result.id), max_age=15695000)
        return response

    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

@app.get('/profile', tags=['Account'])
async def switch_account(response: Response):
    response = RedirectResponse('/login', status_code=302)
    response.delete_cookie('teacher_id')
    response.delete_cookie('student_id')
    return response
