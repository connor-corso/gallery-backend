from sqlalchemy.orm import Session
import math
from fastapi import UploadFile
from . import models, schemas
from ..errorlogger import log_error


def get_all_photos(db: Session):
    return db.query(models.Photo).all()
    
def get_photos_paginated(db: Session, page: int = 0, page_size: int = 30):
    skip = page * page_size
    return db.query(models.Photo).offset(skip).limit(page_size).all()

def add_photo(db: Session, photodata: schemas.Photo):
    if photodata is not None:
        db.add(photodata)
        db.commit()
        db.refresh(photodata)
    else:
        log_error("Empty photo data was received")




