from fastapi import APIRouter, status, Depends, HTTPException, Response
from fastapi_pagination import paginate, Page
from sqlalchemy import exc
from sqlalchemy.orm import Session

from app.database import get_db
from app import models
from app.schemas import TaskResponse, TaskCreate, TaskComplete

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("/", response_model=Page[TaskResponse])
def get_tasks_for_user(db_session: Session = Depends(get_db)):
    owner_id = 3  # Hardcode a user to check as will add login/logout functionality later
    tasks = db_session.query(models.Task)\
        .filter(models.Task.owner_id == owner_id)\
        .all()
    return paginate(tasks)


@router.get("/{id_}", response_model=TaskResponse)
def get_task(id_: int, db_session: Session = Depends(get_db)):
    owner_id = 3  # Hardcode a user to check as will add login/logout functionality later

    task = db_session.query(models.Task)\
        .filter(models.Task.id == id_,
                models.Task.owner_id == owner_id)\
        .first()

    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Task not found with id={id_}')

    return task


@router.post("/", response_model=TaskResponse)
def create_task(task_input: TaskCreate, db_session: Session = Depends(get_db)):
    task_dict = task_input.dict()
    task = models.Task(**task_dict)
    task.owner_id = 3

    db_session.add(task)

    try:
        db_session.commit()
    except exc.SQLAlchemyError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f'Unexpected problem please check the request and try again')

    db_session.refresh(task)

    return task


@router.delete("/{id_}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(id_: int, db_session: Session = Depends(get_db)):
    task = db_session.query(models.Task).get(id_)
    owner_id = 3

    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Task not found id={id_}')

    if task.owner_id != owner_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Not authorised to perform requested action')

    db_session.delete(task)

    try:
        db_session.commit()
    except exc.SQLAlchemyError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f'Unexpected problem please check the request and try again')

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/{id_}", response_model=TaskResponse)
def update_task(id_: int, task_input: TaskCreate, db_session: Session = Depends(get_db)):
    task = db_session.query(models.Task).get(id_)
    owner_id = 3

    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Task not found id={id_}')

    if task.owner_id != owner_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Not authorised to perform requested action')

    for field in ['title', 'description', 'deadline']:
        setattr(task, field, getattr(task_input, field))

    db_session.add(task)

    try:
        db_session.commit()
    except exc.SQLAlchemyError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f'Unexpected problem please check the request and try again')

    db_session.refresh(task)

    return task


@router.put("/complete/{id_}", response_model=TaskResponse)
def complete_task(id_: int, task_input: TaskComplete, db_session: Session = Depends(get_db)):
    task = db_session.query(models.Task).get(id_)
    owner_id = 3

    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Task not found id={id_}')

    if task.owner_id != owner_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Not authorised to perform requested action')

    task.completed = task_input.completed

    db_session.add(task)

    try:
        db_session.commit()
    except exc.SQLAlchemyError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f'Unexpected problem please check the request and try again')

    db_session.refresh(task)

    return task
