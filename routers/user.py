from annotated_types import Annotated
from fastapi import APIRouter, Depends, HTTPException, Path, status
from database import SessionLocal
from models import Todos, Users
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from .auth import get_current_user
from passlib.context import CryptContext

router = APIRouter(
    prefix='/user',
    tags=['user']
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

class UserVerification(BaseModel):
    password: str
    new_password: str = Field(min_length=6)

@router.get("/")
async def get_user(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail='Unauthorized Personel')
    return db.query(Users).filter(Users.id == user.get('id')).first()

@router.put("/password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(user: user_dependency, db: db_dependency, verification: UserVerification):
    if user is None:
        raise HTTPException(status_code=401, detail='Unauthorized Personel')
    user_model = db.query(Users).filter(Users.id == user.get('id')).first()
    if not bcrypt_context.verify(verification.password, user_model.hashed_password):
        raise HTTPException(status_code=401, detail='Error, Mismatch Password')
    user_model.hashed_password = bcrypt_context.hash(verification.new_password)
    db.add(user_model)
    db.commit()
    