# app/messages.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from . import models, schemas, auth, database, crud

router = APIRouter(prefix="/messages", tags=["messages"])

@router.post("/", response_model=schemas.MessageRead)
def send_message(
    message: schemas.MessageCreate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    if message.receiver_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot send message to yourself")
    return crud.send_message(db, sender_id=current_user.id, message=message)

@router.get("/{user_id}", response_model=list[schemas.MessageRead])
def get_conversation(
    user_id: int,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    return crud.get_conversation(db, user1_id=current_user.id, user2_id=user_id, skip=skip, limit=limit)
