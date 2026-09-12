from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from database import db_dependency
from models import Users
from schemas import RegisterModel, CurrentUser, UserOut
from services import auth_service

auth_router = APIRouter(prefix="/auth", tags=["auth"])


@auth_router.post("/login")
def login(db: db_dependency, formData: OAuth2PasswordRequestForm = Depends()):
    return auth_service.verify_login(formData.username, formData.password, db)


@auth_router.post("/register")
def register(formData: RegisterModel, db: db_dependency):
    return auth_service.register_user(formData, db)


@auth_router.get("/me", response_model=UserOut)
def me(db: db_dependency, user: CurrentUser = Depends(auth_service.get_current_user)):
    record = db.query(Users).filter(Users.id == user.user_id).first()
    if not record:
        raise HTTPException(401, "Unauthorized")
    return record
