from annotated_types import Annotated
from fastapi import FastAPI, Depends, HTTPException, Path, status
from database import engine, SessionLocal
import models
from models import Todos
from sqlalchemy.orm import Session

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

@app.get('/')
async def get_all(db: db_dependency):
    return db.query(Todos).all()

@app.get('/todo/{id}', status_code=status.HTTP_200_OK)
async def get_one(db: db_dependency, id: int = Path(gt=0)):
    todo_model = db.query(Todos).filter(Todos.id == id).first()
    if (todo_model):
        return todo_model
    raise HTTPException(status_code=404, detail='Todo not Found')