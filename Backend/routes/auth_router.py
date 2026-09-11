from fastapi import APIRouter, Depends, Request, Response, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from database import db_dependency
from models import Users
from schemas import RegisterModel, CurrentUser, UserOut
from services import auth_service

auth_router = APIRouter(prefix="/auth", tags=["auth"])


@auth_router.post("/login")
def login(
    request: Request,
    response: Response,
    db: db_dependency,
    formData: OAuth2PasswordRequestForm = Depends(),
):
    ua_string = request.headers.get("User-Agent")
    return auth_service.verify_login(
        formData.username, formData.password, db, response, device=ua_string
    )


@auth_router.post("/register")
def register(formData: RegisterModel, db: db_dependency):
    return auth_service.register_user(formData, db)


@auth_router.get("/me", response_model=UserOut)
def me(db: db_dependency, user: CurrentUser = Depends(auth_service.get_current_user)):
    record = db.query(Users).filter(Users.id == user.user_id).first()
    if not record:
        raise HTTPException(401, "Unauthorized")
    return UserOut.model_validate(record)


@auth_router.get("/refresh")
def get_new_token(request: Request, response: Response, db: db_dependency):
    ua_string = request.headers.get("User-Agent")
    refresh_token = request.cookies.get("refresh_token")
    return auth_service.refresh_expired_token(refresh_token, db, response, device=ua_string)


@auth_router.post("/logout")
def logout(request: Request, response: Response, db: db_dependency):
    ua_string = request.headers.get("User-Agent")
    refresh_token = request.cookies.get("refresh_token")
    return auth_service.logout_user(refresh_token, db, response, device=ua_string)
