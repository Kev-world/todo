from annotated_types import Annotated
from fastapi import FastAPI, Depends, HTTPException, Path, status
from database import engine, SessionLocal
import models
from models import Todos
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Dependency Injection
db_dependency = Annotated[Session, Depends(get_db)]

# DTO
class TodoRequest(BaseModel):
    title: str = Field(min_length=3)
    description: str = Field(min_length=3, max_length=100)
    priority: int = Field(gt=0, lt=6)
    complete: bool


@app.get('/')
async def get_all(db: db_dependency):
    return db.query(Todos).all()

@app.get('/todo/{id}', status_code=status.HTTP_200_OK)
async def get_one(db: db_dependency, id: int = Path(gt=0)):
    todo_model = db.query(Todos).filter(Todos.id == id).first()
    if (todo_model):
        return todo_model
    raise HTTPException(status_code=404, detail='Todo not Found')

@app.post('/todo', status_code=status.HTTP_201_CREATED)
async def create(db: db_dependency, req: TodoRequest):
    todo_model = Todos(**req.model_dump())

    db.add(todo_model)
    db.commit()

@app.put('/todo/{id}', status_code=status.HTTP_204_NO_CONTENT)
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

@app.delete('/todo/{id}', status_code=status.HTTP_200_OK)
async def delete(db: db_dependency, id: int = Path(gt=0)):
    todo_model = db.query(Todos).filter(Todos.id == id).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail='Not found')
    
    db.delete(todo_model)
    db.commit()
    return todo_model