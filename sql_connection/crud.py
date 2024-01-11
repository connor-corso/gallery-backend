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
        

# takes a db, a page number, a page size, and optional gallery_id and tag_id and will return a page of photos
def get_photo_info_paginated(db: Session, page: int = 0, page_size: int = 30, gallery_id: int = None, tag_id: int = None):
    skip = page * page_size
    query = db.query(models.Photo)

    if gallery_id is not None:
        db_photos = db.query(models.Photo, models.Gallery).joi
        query = query.join(models.Gallery).filter(models.Gallery.gallery_id == gallery_id)
    
    if tag_id is not None:
        query = query.join(models.Tag).filter(models.Tag.tag_id == tag_id)

    db_photos = query.offset(skip).limit(page_size).all()

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

def get_all_galleries(db: Session):
    return db.query(models.Gallery).all()

def add_photo_to_gallery(db: Session, photo_id: int, gallery_id: int):
    if photo_id is not None and gallery_id is not None:
        photo = db.query(models.Photo).filter(models.Photo.photo_id == photo_id).first()
        gallery = db.query(models.Gallery).filter(models.Gallery.gallery_id == gallery_id).first()
        
        # if we are missing a photo or a gallery than this cant be done
        if not photo or not gallery:
            return False
        
        association_exists = db.query(models.photo_gallery_association).filter_by(
            photo_id = photo_id,
            gallery_id = gallery_id
        ).first()

        if association_exists:
            return False
        
        assoc = models.photo_gallery_association.insert().values(photo_id = photo_id, gallery_id = gallery_id)
        db.execute(assoc)
        db.commit()
        return True

def create_gallery(db: Session, gallery_info: models.Gallery):
    if gallery_info.gallery_title is not None:
        db.add(gallery_info)
        db.commit()
        db.refresh(gallery_info)
    else:
        print("error")
