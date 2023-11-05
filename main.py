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
@app.post("/add-photo/")
async def add_photo(photo: UploadFile, db: Session = Depends(get_db)):
    result = picture_handler.handle_photo(photo,db)
    if result == 0:
        return {"success": "photo was accepted"}
    elif result == 10:
        return {"error": "photo was rejected"}
    else:
        return {"result": str(result)}

@app.get("/get-photo/")
async def get_photo(db: Session = Depends(get_db)):
    photos = crud.get_photos_paginated(db, 0, 1)
    if photos:
        return FileResponse(photos[0].image_path)
    else:
        return {"error": "No photo found"}

