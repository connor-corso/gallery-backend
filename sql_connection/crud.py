from sqlalchemy.orm import Session
from . import models, schemas
from typing import Optional
from pydantic import TypeAdapter
#from ..errorlogger import log_error


def get_all_photos(db: Session):
    return db.query(models.Photo).all()
    
def get_photos_paginated(db: Session, page: int = 0, page_size: int = 30) -> list[schemas.Photo]:
    skip = page * page_size
    db_photos = db.query(models.Photo).offset(skip).limit(page_size).all()
    if db_photos:
        pydantic_photos = [TypeAdapter[schemas.Photo].validate_python(photo) for photo in db_photos]
        return pydantic_photos
    return None
        
def get_photo_info_paginated(db: Session, page: int = 0, page_size: int = 30):
    skip = page * page_size
    db_photos = db.query(models.Photo).offset(skip).limit(page_size).all()
    if db_photos:
        return db_photos
    return None

def get_photo_info_from_id(db: Session, photo_id: int):
    if photo_id:
        photo_info = db.query(models.Photo).filter(models.Photo.photo_id == photo_id).first()
        return photo_info
    return None

def get_one_photo(db: Session) -> Optional[schemas.Photo]:
    db_photo = db.query(models.Photo).first()
    #pydantic_photo = TypeAdapter[schemas.Photo].validate_python(db_photo)
    if db_photo:
        print(db_photo)
        return db_photo
        #return pydantic_photo
    return None
        

def add_photo(db: Session, photodata: schemas.Photo):
    if photodata.photo_path is not None and photodata.photo_title is not None:
        # create the schema with the information that we have in it, then dump it to the database
        #photodata = schemas.PhotoCreate(photo_title=photodata.photo_title, photo_path=photodata.photo_path)
        
        # .dict is said to be deprecated
        db_photo = models.Photo(**photodata.model_dump())
        #print(str(**photodata.model_dump()))
        #db_photo = models.Photo(**photodata.dict())
        # dump the record to the db and refresh
        db.add(db_photo)
        db.commit()
        db.refresh(db_photo)
    else:
        print("error")
        #log_error("Empty photo data was received")




