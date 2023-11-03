#/usr/bin/python3

##############################
# 
# Written by Connor Corso
# 
##############################

import os
from fastapi import Depends, FastAPI, HTTPException, UploadFile
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
import datetime

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
async def add_photo(photo: UploadFile):
    if photo.content_type != ("image/jpeg" or "image/png" or "image/webp"):
        file_path = os.path.join(PHOTO_REJECTS_DIRECTORY,photo.filename)
        
        raise HTTPException(400, detail="Invalid Image")
    
    return {"filename": photo.filename}

