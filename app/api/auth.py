from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.user import UserCreate, UserLogin, UserWithToken
from app.db.session import SessionLocal
from app.cruds import user as user_crud
from app.services.auth import create_access_token
from app.services.auth import get_current_user
from app.models.user import User
from app.schemas.user import UserOut

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/sign-up/", response_model=UserWithToken, tags=["Аутентификация"])
def sign_up(user_data: UserCreate, db: Session = Depends(get_db)):
    db_user = user_crud.get_user_by_email(db, user_data.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = user_crud.create_user(db, user_data)
    token = create_access_token({"sub": user.email})
    return {"id": user.id, "email": user.email, "token": token}


@router.post("/login/", response_model=UserWithToken, tags=["Аутентификация"])
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    user = user_crud.get_user_by_email(db, user_data.email)
    if not user or not user_crud.verify_password(user_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token({"sub": user.email})
    return {"id": user.id, "email": user.email, "token": token}

@router.get("/users/me/", response_model=UserOut, tags=["Аутентификация"])
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user