#/usr/bin/python3

##############################
# 
# Written by Connor Corso
# 
##############################

import os
from fastapi import Depends, FastAPI, HTTPException, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from sql_connection import crud, models, schemas
from sql_connection.database import SessionLocal, engine
import datetime
import imagehandler


picture_handler = imagehandler.PhotoHandler()
models.Base.metadata.create_all(bind=engine)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



#from sql_connection import crud, models, schemas
#from sql_connection.database import SessionLocal, engine

# fast api setup
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)




# this is where we will define all of our endpoints that can be accessed


# test curl command 
# curl -X 'POST' 'http://127.0.0.1:8080/add-photo/3/' -H 'Content-Type: multipart/form-data' -F 'file=@/home/connor/connors things/projects/ccorso website/public/images/droppyicon.png'
# this endpoint listens on /add-photo/ and will accept form/multipart data with an image with MIME type image/[jpeg|webp|png], if the uploaded file doesn't meet the standards then it gets dumped to a rejects directory that will have to be manually sorted




#################################################################################
# Add photo methods

@app.post("/add-photo/")
async def add_photo(photo: UploadFile, db: Session = Depends(get_db)):
    result = picture_handler.handle_photo(photo,db)
    if result == 0:
        return {"success": "photo was accepted"}
    elif result == 10:
        return {"error": "photo was rejected"}
    else:
        return {"result": str(result)}




##################################################################################
# Get photo methods

@app.get("/get-photo-info-paginated/")
async def get_photo_info_paginated(db: Session = Depends(get_db), page_size: int= 30, page: int = 0, gallery_id: int = None, tag_id: int = None,favorite:int = 0):
    
    photo_info = crud.get_photo_info_paginated(db, page=page, page_size=page_size, gallery_id=gallery_id, tag_id=tag_id, favorite=favorite)
    if photo_info:
        return photo_info
    raise HTTPException(status_code=404, detail="No photoids found")


@app.get("/get-photo-by-id/{photo_id}/")
async def get_photo_by_id(photo_id: int, db: Session = Depends(get_db)):
    photo_info = crud.get_photo_info_from_id(db, photo_id=photo_id)
    if photo_info:
        return FileResponse(photo_info.photo_path)
    raise HTTPException(status_code=404, detail="No matching photo was found")
    

@app.get("/get-thumbnail-by-id/{photo_id}/")
async def get_thumbnail_by_id(photo_id: int, db: Session = Depends(get_db)):
    print(f"Getting thumbnail for image: {photo_id}")
    photo_info = crud.get_photo_info_from_id(db, photo_id=photo_id)
    if photo_info:
        return FileResponse(photo_info.thumbnail_path)
    raise HTTPException(status_code=404, detail="No matching photo was found")

@app.get("/get-motion-photo-by-id/{photo_id}/")
async def get_photo_by_id(photo_id: int, db: Session = Depends(get_db)):
    photo_info = crud.get_photo_info_from_id(db, photo_id=photo_id)
    # if the photoinfo exists and the photoinfo.motionphoto bool is true then return the motion photo found
    if photo_info and photo_info.motion_photo:
        return FileResponse(photo_info.motion_photo_path,media_type="video/mp4")
    raise HTTPException(status_code=404, detail="The photo does not have a motion photo with it or the photo was not found")

###################################################################################
# Favorite methods

@app.put("/toggle-favorite/{photo_id}/")
async def toggle_favorite(photo_id: int, db: Session = Depends(get_db)):
    crud.toggle_favorite(db, photo_id=photo_id)


###################################################################################
# Gallery methods

@app.post("/create-gallery/{gallery_title}/")
async def create_gallery(gallery_title: str, db: Session = Depends(get_db)):
    print(gallery_title)
    if gallery_title != "":
        gallery_info = models.Gallery(gallery_title = gallery_title)
        crud.create_gallery(db, gallery_info=gallery_info)
        return
    raise HTTPException(status_code=400, detail="Please provide a gallery title")


@app.get("/get-galleries/")
async def get_galleries(db: Session = Depends(get_db)):
    gallery_infos = crud.get_all_galleries(db)
    if gallery_infos:
        return gallery_infos
    raise HTTPException(status_code=400, detail="No galleries exist")


@app.put("/add-photo-to-gallery/{photo_id}/{gallery_id}/")
async def add_photo_to_gallery(photo_id: int = None, gallery_id: int = None, db: Session = Depends(get_db)):
    print(f"photo_id:{photo_id}")
    print(f"gallery_id:{gallery_id}")
    if photo_id is not None and gallery_id is not None:
        crud.add_photo_to_gallery(db, photo_id, gallery_id)
        return
    raise HTTPException(status_code=400, detail="Need to provide a photoid and a galleryid")

###################################################################################
#reprocessing methods
@app.put("/reprocess-all-photos/")
async def reprocess_all_photos(db: Session = Depends(get_db)):
    photos = crud.get_all_photos(db)
    num_photos = 0
    for photo in photos:
        picture_handler.reprocess_photo(photo,db)
        num_photos +=1
    return {"processed" : num_photos}

@app.put("/reprocess-photo-by-id/{photo_id}/")
async def reprocess_photo_by_id(photo_id:int, db: Session = Depends(get_db)):
    photo = crud.get_photo_info_from_id(db,photo_id)
    result = picture_handler.reprocess_photo(photo,db)
    if result == 0:
        return {"success": "photo was reprocessed"}
    else:
        return {"error" : str(result)}


# @app.get("/get-photos-paginated/")
# async def get_photos_paginated(db: Session = Depends(get_db), page_size: int = 30, page: int = 0):
#     photos = crud.get_photos_paginated(db, page=page, page_size=page_size)
#     if photos:
#         pass

# @app.get("/get-one-photo/")
# async def get_one_photo(db: Session = Depends(get_db)):
#     photo = crud.get_one_photo(db)
#     if photo:
#         print(str(photo))
#         print(str(photo.photo_path))
#         if os.path.isfile(photo.photo_path):
#             return FileResponse(photo.photo_path)
#         else:
#             raise HTTPException(status_code=404, detail="Photo file not found at that filepath")
#     else:
#         raise HTTPException(status_code=404, detail="No photo found")
