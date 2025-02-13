from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from . import auth, crud, dependencies
from . import schemas
from .database import engine, Base
from fastapi.security import OAuth2PasswordRequestForm
from typing import List
from datetime import timedelta
from .auth import verify_password, create_access_token


Base.metadata.create_all(bind=engine)

app = FastAPI()


def authenticate_user(db: Session, username: str, password: str):
    user = crud.get_user_by_username(db, username=username)
    if not user or not verify_password(password, user.password):
        return False
    return user


@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(dependencies.get_db)):
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_password = auth.get_password_hash(user.password)
    user.password = hashed_password
    return crud.create_user(db=db, user=user)

@app.get("/users/", response_model=List[schemas.User])
def read_users(skip: int = 0, limit: int = 10, sort_by: str = 'username', db: Session = Depends(dependencies.get_db)):
    users = crud.get_users(db, skip=skip, limit=limit, sort_by=sort_by)
    return users

@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(dependencies.get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@app.get("/users/me/", response_model=schemas.User)
def read_users_me(current_user: schemas.User = Depends(dependencies.get_current_active_user)):
    return current_user

@app.get("/admin/", response_model=List[schemas.User])
def read_users_admin(skip: int = 0, limit: int = 10, db: Session = Depends(dependencies.get_db),
                     current_user: schemas.User = Depends(dependencies.get_current_active_admin)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


@app.put("/users/{user_id}", response_model=schemas.User)
def update_user(user_id: int, user: schemas.UserCreate, db: Session = Depends(dependencies.get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return crud.update_user(db=db, user_id=user_id, user=user)

@app.delete("/users/{user_id}", response_model=schemas.User)
def delete_user(user_id: int, db: Session = Depends(dependencies.get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return crud.delete_user(db=db, user_id=user_id)

@app.post("/token", response_model=schemas.Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(dependencies.get_db)):
    user = authenticate_user(db, username=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

