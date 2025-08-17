# app/crud.py
from sqlalchemy.orm import Session
from sqlalchemy.orm import joinedload
from . import models, schemas

def create_post(db: Session, post: schemas.PostCreate, author_id: int):
    db_post = models.Post(content=post.content, author_id=author_id)
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

