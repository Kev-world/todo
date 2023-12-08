from fastapi import APIRouter, Depends
from pydantic import BaseModel
from models import Users
from passlib.context import CryptContext
from annotated_types import Annotated
from sqlalchemy.orm import Session
from database import SessionLocal

router = APIRouter()

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

# DTO
class CreateUserRequest(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str
    password: str
    role: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

@router.post('/auth/')
async def create_user(db: db_dependency, dto: CreateUserRequest):
    user_model = Users(
        email = dto.email,
        username = dto.username,
        first_name = dto.first_name,
        last_name = dto.last_name,
        hashed_password = bcrypt_context.hash(dto.password),
        role = dto.role,
        is_active=True
    )
    
    db.add(user_model)
    db.commit()
    