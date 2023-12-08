from annotated_types import Annotated
from fastapi import APIRouter, Depends, HTTPException, Path, status
from database import SessionLocal
from models import Todos
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from .auth import get_current_user

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Dependency Injection
db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

# DTO
class TodoRequest(BaseModel):
    title: str = Field(min_length=3)
    description: str = Field(min_length=3, max_length=100)
    priority: int = Field(gt=0, lt=6)
    complete: bool


@router.get('/')
async def get_all(db: db_dependency):
    return db.query(Todos).all()

@router.get('/todo/{id}', status_code=status.HTTP_200_OK)
async def get_one(db: db_dependency, id: int = Path(gt=0)):
    todo_model = db.query(Todos).filter(Todos.id == id).first()
    if (todo_model):
        return todo_model
    raise HTTPException(status_code=404, detail='Todo not Found')

@router.post('/todo', status_code=status.HTTP_201_CREATED)
async def create(user: user_dependency, db: db_dependency, req: TodoRequest):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    todo_model = Todos(**req.model_dump(), owner_id=user.get('id'))

    db.add(todo_model)
    db.commit()

@router.put('/todo/{id}', status_code=status.HTTP_204_NO_CONTENT)
async def update(db: db_dependency, req: TodoRequest, id: int = Path(gt=0)):
    todo_model = db.query(Todos).filter(Todos.id == id).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail='Not found')
    
    todo_model.title = req.title
    todo_model.description = req.description
    todo_model.priority = req.priority
    todo_model.complete = req.complete

    db.add(todo_model)
    db.commit()

@router.delete('/todo/{id}', status_code=status.HTTP_200_OK)
async def delete(db: db_dependency, id: int = Path(gt=0)):
    todo_model = db.query(Todos).filter(Todos.id == id).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail='Not found')
    
    db.delete(todo_model)
    db.commit()
    return todo_model