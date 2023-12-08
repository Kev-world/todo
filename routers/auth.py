from fastapi import APIRouter
from pydantic import BaseModel
from models import Users
from passlib.context import CryptContext

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

@router.post('/auth/')
async def create_user(dto: CreateUserRequest):
    user_model = Users(
        email = dto.email,
        username = dto.username,
        first_name = dto.first_name,
        last_name = dto.last_name,
        hashed_password = bcrypt_context.hash(dto.password),
        role = dto.role,
        is_active=True
    )
    return user_model