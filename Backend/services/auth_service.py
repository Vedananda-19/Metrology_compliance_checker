from fastapi import Depends, HTTPException, Response
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from models import Users, RefreshTokens
from schemas import RegisterModel, CurrentUser
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from database import db_dependency
from jose import jwt, JWTError, ExpiredSignatureError
from config import JWT_SECRET_KEY, ALGORITHM, ACCESS_TOKEN_MINUTES, REFRESH_TOKEN_DAYS
import hashlib
import hmac
import uuid

OAuth2Scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def register_user(formData: RegisterModel, db: Session):
    if formData.password != formData.confirmPassword:
        raise HTTPException(400, "Passwords Dont match")
    if len(formData.password) < 6:
        raise HTTPException(400, "Password must be at least 6 characters")
    existing_user = db.query(Users).filter(Users.username == formData.username).first()
    if existing_user:
        raise HTTPException(400, "Username Already Exists")

    new_user = Users(
        username=formData.username,
        password=pwd_context.hash(formData.password),
        full_name=formData.full_name,
        designation=formData.designation,
        office=formData.office,
    )
    db.add(new_user)
    db.commit()

    return {"message": "Inspector registered successfully"}


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def create_access_token(user: Users):
    expiry = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_MINUTES)
    encode_data = {"id": user.id, "sub": user.username, "exp": expiry}
    token: str = jwt.encode(encode_data, JWT_SECRET_KEY, algorithm=ALGORITHM)
    return {"access_token": token, "token_type": "bearer"}


def create_refresh_token(user: Users, db: Session, device: str):
    expiry = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_DAYS)
    encode_data = {
        "id": user.id,
        "sub": user.username,
        "exp": expiry,
        "jti": str(uuid.uuid4()),
    }
    token: str = jwt.encode(encode_data, JWT_SECRET_KEY, algorithm=ALGORITHM)

    db.query(RefreshTokens).filter(
        RefreshTokens.user_id == user.id, RefreshTokens.device == device
    ).delete()
    db.add(RefreshTokens(token=hash_token(token), device=device, user_id=user.id))
    db.commit()
    return token


def set_refresh_cookie(response: Response, token: str):
    response.set_cookie(
        "refresh_token",
        token,
        httponly=True,
        samesite="lax",
        secure=False,
        path="/auth",
        max_age=REFRESH_TOKEN_DAYS * 24 * 60 * 60,
    )


def verify_login(username: str, password: str, db: Session, response: Response, device: str):
    user = db.query(Users).filter(Users.username == username).first()
    if not user:
        raise HTTPException(400, "Username does not exist")
    if not pwd_context.verify(password, user.password):
        raise HTTPException(400, "Invalid Credentials")

    set_refresh_cookie(response, create_refresh_token(user, db, device))
    return create_access_token(user)


def verify_token(db: db_dependency, token: str = Depends(OAuth2Scheme)) -> CurrentUser:
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("id")
        username = payload.get("sub")
        if user_id is None:
            raise HTTPException(401, "Unauthorized")
        return CurrentUser(user_id=user_id, username=username)
    except ExpiredSignatureError:
        raise HTTPException(401, "Expired Token")
    except JWTError:
        raise HTTPException(401, "Unauthorized")


def get_current_user(user: CurrentUser = Depends(verify_token)):
    return user


def verify_refresh_token(refresh_token: str, user_id: str, db: Session, device: str):
    stored = (
        db.query(RefreshTokens)
        .filter(RefreshTokens.user_id == user_id, RefreshTokens.device == device)
        .first()
    )
    if stored is None:
        return False
    return hmac.compare_digest(hash_token(refresh_token), stored.token)


def refresh_expired_token(refresh_token: str, db: Session, response: Response, device: str):
    if not refresh_token:
        raise HTTPException(401, "Unauthorized")
    try:
        payload = jwt.decode(refresh_token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(401, "Unauthorized")

    user_id = payload.get("id")
    if not verify_refresh_token(refresh_token, user_id, db, device):
        raise HTTPException(401, "Unauthorized")

    user = db.query(Users).filter(Users.id == user_id).first()
    if not user:
        raise HTTPException(401, "Unauthorized")

    set_refresh_cookie(response, create_refresh_token(user, db, device))
    return create_access_token(user)


def logout_user(refresh_token: str, db: Session, response: Response, device: str):
    response.delete_cookie("refresh_token", path="/auth", samesite="lax")
    if not refresh_token:
        return {"message": "Logged Out Successfully"}
    try:
        payload = jwt.decode(refresh_token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
        db.query(RefreshTokens).filter(
            RefreshTokens.user_id == payload.get("id"), RefreshTokens.device == device
        ).delete()
        db.commit()
    except JWTError:
        pass
    return {"message": "Logged Out Successfully"}
