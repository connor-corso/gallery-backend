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

def add_photo(db: Session, file_path: str, original_filename: str):
    if file_path is not None and original_filename is not None:
        # create the schema with the information that we have in it, then dump it to the database
        photodata = schemas.PhotoCreate(photo_title=original_filename, image_path=file_path)
        
        # dump the record to the db and refresh
        db.add(photodata)
        db.commit()
        db.refresh(photodata)
    else:
        log_error("Empty photo data was received")




