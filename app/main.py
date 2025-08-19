# app/main.py
from fastapi import FastAPI, Depends, HTTPException
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from . import models, schemas, crud, database, auth, users
from .models import RevokedToken
from fastapi.middleware.cors import CORSMiddleware


models.Base.metadata.create_all(bind=database.engine)
app = FastAPI(title="Microblog API with Auth")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)
app.include_router(users.router)


@app.get("/posts/", response_model=list[schemas.PostRead])
def read_posts(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    posts = crud.get_posts(db, author_id=current_user.id, skip=skip, limit=limit)
    return posts

@app.get("/posts/{post_id}", response_model=schemas.PostRead)
def read_post(
    post_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    post = crud.get_post(db, post_id=post_id)
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return post

@app.post("/posts/", response_model=schemas.PostRead)
def create_post(
    post: schemas.PostCreate,
    request: Request,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    try:
        return crud.create_post(db, post, author_id=current_user.id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

@app.put("/posts/{post_id}", response_model=schemas.PostRead)
def edit_post(post_id: int, post: schemas.PostCreate, db: Session = Depends(database.get_db), current_user=Depends(auth.get_current_user)):
    updated = crud.update_post(db, post_id, post, current_user.id)
    if updated == "not_found":
        raise HTTPException(status_code=404, detail="Post not found")
    elif updated == "unauthorized":
        raise HTTPException(status_code=403, detail="Not authorized to edit this post")
    return updated

@app.delete("/posts/{post_id}")
def delete_post(post_id: int, db: Session = Depends(database.get_db), current_user=Depends(auth.get_current_user)):
    deleted = crud.delete_post(db, post_id, current_user.id)
    if deleted == "not_found":
        raise HTTPException(status_code=404, detail="Post not found")
    elif deleted == "unauthorized":
        raise HTTPException(status_code=403, detail="Not authorized to delete this post")
    return JSONResponse(content={"message": "Delete successfully"}, status_code=200)

@app.get("/verify-token")
async def verify_token(current_user: models.User = Depends(auth.get_current_user)):
    return {
        "message": "Token is valid", 
        "user": current_user.username,
        "id": current_user.id  # Add this line to include the user ID
    }

@app.post("/logout")
def logout(
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
    db: Session = Depends(database.get_db)
):
    token = credentials.credentials

    # Cleanup before checking
    auth.cleanup_expired_revoked_tokens(db)

    # Check if token already revoked
    already = db.query(RevokedToken).filter(RevokedToken.token == token).first()
    if already:
        return JSONResponse(content={"message": "Already logged out"}, status_code=200)

    revoked = RevokedToken(token=token)
    db.add(revoked)
    db.commit()
    return JSONResponse(content={"message": "Logout successful. Token revoked."}, status_code=200)
