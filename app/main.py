from fastapi import Depends, FastAPI, HTTPException,Response
from sqlalchemy.orm import Session

from . import models, schemas
from app.user_management import User, Items
from .database import SessionLocal, engine
from .schemas import UserUpdate

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dependency

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = User.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return User.create_user(db=db, user=user)


@app.get("/users/", response_model=list[schemas.User])
def users_list(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    user = User.get_users(db, skip=skip, limit=limit)
    return user


@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    user = User.get_user(db, user_id=user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.post("/users/{user_id}/items/", response_model=schemas.Item)
def create_item_for_user(
    user_id: int, item: schemas.ItemCreate, db: Session = Depends(get_db)
):
    return User.create_user_item(db=db, item=item, user_id=user_id)


@app.get("/items/", response_model=list[schemas.Item])
def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items = User.get_items(db, skip=skip, limit=limit)
    return items

@app.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = User.get_user(db, user_id=user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return Response(status_code=204)


@app.put("/users/{user_id}")
async def update_user(user_id: int, updated_data: UserUpdate, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    for field, value in updated_data.dict().items():
        if hasattr(user, field) and value:
            setattr(user, field, value)
    db.commit()
    db.refresh(user)
    return user

@app.get("/users/items/{items_id}",response_model=schemas.Item)
def read_item(items_id: int, db: Session = Depends(get_db)):
    item = Items.get_item(db, item_id=items_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@app.get("/users/items/{items_id}",response_model=schemas.Item)
def read_item(items_id: int, db: Session = Depends(get_db)):
    item = Items.get_item(db, item_id=items_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item