from sqlalchemy.orm import Session
import math
from fastapi import UploadFile
from . import models, schemas
#from ..errorlogger import log_error


def get_all_photos(db: Session):
    return db.query(models.Photo).all()
    
def get_photos_paginated(db: Session, page: int = 0, page_size: int = 30):
    skip = page * page_size
    return db.query(models.Photo).offset(skip).limit(page_size).all()

def add_photo(db: Session, photodata: schemas.Photo):
    if photodata.photo_path is not None and photodata.photo_title is not None:
        # create the schema with the information that we have in it, then dump it to the database
        #photodata = schemas.PhotoCreate(photo_title=photodata.photo_title, photo_path=photodata.photo_path)
        db_photo = models.Photo(**photodata.dict())
        # dump the record to the db and refresh
        db.add(db_photo)
        db.commit()
        db.refresh(db_photo)
    else:
        print("error")
        #log_error("Empty photo data was received")




