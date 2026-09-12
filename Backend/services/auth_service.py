from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from models import Users
from schemas import RegisterModel, CurrentUser
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from database import db_dependency
from jose import jwt, JWTError, ExpiredSignatureError
from config import JWT_SECRET_KEY, ALGORITHM, ACCESS_TOKEN_HOURS

OAuth2Scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def register_user(formData: RegisterModel, db: Session):
    if formData.password != formData.confirmPassword:
        raise HTTPException(400, "Passwords Dont match")
    if len(formData.password) < 6:
        raise HTTPException(400, "Password must be at least 6 characters")
    if db.query(Users).filter(Users.username == formData.username).first():
        raise HTTPException(400, "Username Already Exists")

    db.add(
        Users(
            username=formData.username,
            password=pwd_context.hash(formData.password),
            full_name=formData.full_name,
        )
    )
    db.commit()
    return {"message": "Inspector registered successfully"}


def create_access_token(user: Users):
    expiry = datetime.now(timezone.utc) + timedelta(hours=ACCESS_TOKEN_HOURS)
    token = jwt.encode({"id": user.id, "sub": user.username, "exp": expiry}, JWT_SECRET_KEY, algorithm=ALGORITHM)
    return {"access_token": token, "token_type": "bearer"}


def verify_login(username: str, password: str, db: Session):
    user = db.query(Users).filter(Users.username == username).first()
    if not user:
        raise HTTPException(400, "Username does not exist")
    if not pwd_context.verify(password, user.password):
        raise HTTPException(400, "Invalid Credentials")
    return create_access_token(user)


def verify_token(db: db_dependency, token: str = Depends(OAuth2Scheme)) -> CurrentUser:
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("id")
        if user_id is None:
            raise HTTPException(401, "Unauthorized")
        return CurrentUser(user_id=user_id, username=payload.get("sub"))
    except ExpiredSignatureError:
        raise HTTPException(401, "Expired Token")
    except JWTError:
        raise HTTPException(401, "Unauthorized")


def get_current_user(user: CurrentUser = Depends(verify_token)):
    return user
