from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import models
import schemas
from database import get_db
from fastapi.security import OAuth2PasswordBearer
from fastapi.security import OAuth2PasswordRequestForm
from jose import JWTError

load_dotenv()

router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


class Settings:
    SECRET_KEY = os.getenv("SECRET_KEY", "fallbacksecret")
    ALGORITHM = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES = int(
        os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', 60)
    )


settings = Settings()


@router.post("/register")
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):

    existing_user = db.query(models.User).filter(
        models.User.email == user.email
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already exists"
        )

    hashed_password = pwd_context.hash(user.password)

    new_user = models.User(
        name=user.name,
        email=user.email,
        password=hashed_password,
        role=user.role
    )

    db.add(new_user)
    db.commit()

    return {"message": "User registered successfully"}


def create_access_token(data: dict):

    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )

    return encoded_jwt


# @router.post("/login")
# def login(data: schemas.LoginSchema, db: Session = Depends(get_db)):

#     user = db.query(models.User).filter(
#         models.User.email == data.email
#     ).first()

#     if not user:
#         raise HTTPException(
#             status_code=400,
#             detail="Invalid Email"
#         )

#     if not pwd_context.verify(data.password, user.password):
#         raise HTTPException(
#             status_code=400,
#             detail="Invalid Password"
#         )

#     access_token = create_access_token(
#         data={
#             "user_id": user.id,
#             "email": user.email,
#             "role": user.role
#         }
#     )

#     return {
#         "access_token": access_token,
#         "token_type": "bearer",
#         "role": user.role
#     }
@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):

    user = db.query(models.User).filter(
        models.User.email == form_data.username
    ).first()

    if not user:
        raise HTTPException(
            status_code=400,
            detail="Invalid Email"
        )

    if not pwd_context.verify(form_data.password, user.password):
        raise HTTPException(
            status_code=400,
            detail="Invalid Password"
        )

    access_token = create_access_token(
        data={
            "user_id": user.id,
            "email": user.email,
            "role": user.role
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": user.role
    }

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):

    credentials_exception = HTTPException(
        status_code=401,
        detail="Invalid token"
    )

    try:

        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )

        user_id = payload.get("user_id")

        if user_id is None:
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    user = db.query(models.User).filter(
        models.User.id == user_id
    ).first()

    if user is None:
        raise credentials_exception

    return user


@router.get("/me")
def get_me(current_user: models.User = Depends(get_current_user)):

    return {
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
        "role": current_user.role
    }


def require_role(required_role: str):

    def role_checker(
        current_user: models.User = Depends(get_current_user)
    ):

        if current_user.role != required_role:
            raise HTTPException(
                status_code=403,
                detail="Access Denied"
            )

        return current_user

    return role_checker