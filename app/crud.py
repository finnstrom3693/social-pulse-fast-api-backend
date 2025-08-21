# app/crud.py
from sqlalchemy.orm import Session
from sqlalchemy.orm import joinedload
from . import models, schemas
from sqlalchemy import or_, and_

def create_post(db: Session, post: schemas.PostCreate, author_id: int):
    db_post = models.Post(
        content=post.content,
        image_url=post.image_url,   # <-- save image URL
        author_id=author_id
    )
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post

def get_posts(db: Session, author_id: int, skip: int = 0, limit: int = 10):
    return (
        db.query(models.Post)
        .options(joinedload(models.Post.author))
        .filter(models.Post.author_id == author_id)
        .order_by(models.Post.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

def get_post(db: Session, post_id: int):
    return db.query(models.Post).options(
        joinedload(models.Post.author)  # Changed from author_obj to author
    ).filter(models.Post.id == post_id).first()

def update_post(db: Session, post_id: int, post_update: schemas.PostCreate, user_id: int):
    db_post = get_post(db, post_id)
    if db_post is None:
        return "not_found"
    if db_post.author_id != user_id:
        return "unauthorized"
    db_post.content = post_update.content
    db_post.image_url = post_update.image_url  # <-- update image URL too
    db.commit()
    db.refresh(db_post)
    return db_post

def delete_post(db: Session, post_id: int, user_id: int):
    db_post = get_post(db, post_id)
    if db_post is None:
        return "not_found"
    if db_post.author_id != user_id:
        return "unauthorized"
    db.delete(db_post)
    db.commit()
    return db_post

# ---- Messages ----
def send_message(db: Session, sender_id: int, message: schemas.MessageCreate):
    # Verify receiver exists
    receiver = db.query(models.User).filter(models.User.id == message.receiver_id).first()
    if not receiver:
        raise ValueError("Receiver not found")
    
    db_message = models.Message(
        sender_id=sender_id,
        receiver_id=message.receiver_id,
        content=message.content
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    
    # Get sender and receiver usernames
    sender = db.query(models.User).filter(models.User.id == sender_id).first()
    
    # Return message with usernames
    return schemas.MessageRead(
        id=db_message.id,
        sender_id=db_message.sender_id,
        receiver_id=db_message.receiver_id,
        content=db_message.content,
        created_at=db_message.created_at,
        sender_username=sender.username,
        receiver_username=receiver.username
    )

def get_conversation(db: Session, user1_id: int, user2_id: int, skip: int = 0, limit: int = 50):
    # Get messages between two users
    messages = (
        db.query(models.Message)
        .filter(
            or_(
                and_(models.Message.sender_id == user1_id, models.Message.receiver_id == user2_id),
                and_(models.Message.sender_id == user2_id, models.Message.receiver_id == user1_id)
            )
        )
        .order_by(models.Message.created_at.asc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    
    # Get user information for username mapping
    users = db.query(models.User).filter(
        or_(models.User.id == user1_id, models.User.id == user2_id)
    ).all()
    
    user_map = {user.id: user.username for user in users}
    
    # Convert to MessageRead schema with usernames
    result = []
    for message in messages:
        result.append(schemas.MessageRead(
            id=message.id,
            sender_id=message.sender_id,
            receiver_id=message.receiver_id,
            content=message.content,
            created_at=message.created_at,
            sender_username=user_map.get(message.sender_id, "Unknown"),
            receiver_username=user_map.get(message.receiver_id, "Unknown")
        ))
    
    return result

def get_explore_posts(db: Session, skip: int = 0, limit: int = 10):
    return (
        db.query(models.Post)
        .options(joinedload(models.Post.author))
        .order_by(models.Post.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )