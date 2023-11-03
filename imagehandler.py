import os
from fastapi import UploadFile
from uuid import uuid4
import queue
from errorlogger import log_error
from sql_connection import crud
class PhotoHandler():
    def __init__(self,db):
        self.processing_queue = queue.Queue()
        self.db = db
        
        # setup all the picture directories by checking to see if an environment variable exists for that and if not use the default
        
        self.PHOTO_ROOT_DIRECTORY = os.getenv("PHOTO_ROOT_DIRECTORY")
        if self.PHOTO_ROOT_DIRECTORY is None:
            self.PHOTO_ROOT_DIRECTORY = "./pictures"                                 ## the root folder of all the pics

        
        self.PHOTO_CACHE_DIRECTORY = os.getenv("PHOTO_CACHE_DIRECTORY")
        if self.PHOTO_CACHE_DIRECTORY is None:
            self.PHOTO_CACHE_DIRECTORY = "./pictures/cache"                          ## the folder where pics will have their icons placed after being processed
        

        self.PHOTO_UPLOAD_DIRECTORY = os.getenv("PHOTO_UPLOAD_DIRECTORY")
        if self.PHOTO_UPLOAD_DIRECTORY is None:
            self.PHOTO_UPLOAD_DIRECTORY = "./pictures/uploads"                       ## the folder where new pics will get uploaded before getting processed
            

        self.PHOTO_REJECTS_DIRECTORY = os.getenv("PHOTO_REJECTS_DIRECTORY")
        if self.PHOTO_REJECTS_DIRECTORY is None:
            self.PHOTO_REJECTS_DIRECTORY = "./pictures/rejects"                      ## the folder where reject photos will go
            
        self.PHOTO_ORIGINALS_DIRECTORY = os.getenv("PHOTO_ORIGINALS_DIRECTORY")
        if self.PHOTO_ORIGINALS_DIRECTORY is None:
            self.PHOTO_ORIGINALS_DIRECTORY = "./pictures/originals"                  ## the folder where the original photos will be moved to after being processed
            
        self.PHOTO_MOTION_PHOTOS_DIRECTORY = os.getenv("PHOTO_MOTION_PHOTOS_DIRECTORY")
        if self.PHOTO_MOTION_PHOTOS_DIRECTORY is None:
            self.PHOTO_MOTION_PHOTOS_DIRECTORY = "./pictures/motion_photos"          ## the folder where the motion part of motion photos will go
            
        self.PHOTO_PROCESSED_PHOTOS_DIRECTORY = os.getenv("PHOTO_PROCESSED_PHOTOS_DIRECTORY")
        if self.PHOTO_PROCESSED_PHOTOS_DIRECTORY is None:
            self.PHOTO_PROCESSED_PHOTOS_DIRECTORY = "./pictures/processed_photos"    ## the folder where processed photos will go
            

        # create all the directories if they don't exist
        if not os.path.exists(self.PHOTO_ROOT_DIRECTORY):
            os.makedirs(self.PHOTO_ROOT_DIRECTORY)
        if not os.path.exists(self.PHOTO_CACHE_DIRECTORY):
            os.makedirs(self.PHOTO_CACHE_DIRECTORY)
        if not os.path.exists(self.PHOTO_UPLOAD_DIRECTORY):
            os.makedirs(self.PHOTO_UPLOAD_DIRECTORY)
        if not os.path.exists(self.PHOTO_REJECTS_DIRECTORY):
            os.makedirs(self.PHOTO_REJECTS_DIRECTORY)
        if not os.path.exists(self.PHOTO_ORIGINALS_DIRECTORY):
            os.makedirs(self.PHOTO_ORIGINALS_DIRECTORY)
        if not os.path.exists(self.PHOTO_MOTION_PHOTOS_DIRECTORY):
            os.makedirs(self.PHOTO_MOTION_PHOTOS_DIRECTORY)
        if not os.path.exists(self.PHOTO_PROCESSED_PHOTOS_DIRECTORY):
            os.makedirs(self.PHOTO_PROCESSED_PHOTOS_DIRECTORY)

    def _add_reject(self,filepath: str,original_filename: str):
        log_error(f"file: {original_filename} ({filepath}) was a reject")
        

    def _add_goodphoto(self,filepath: str):
        crud.add_photo(self.db,filepath)

    def _enqueue_processing(self):
        pass

    def handle_photo(self, upload_file: UploadFile):
        # save the upload file to a temp file that can be thrown in the queue
        original_filename = upload_file.filename
        # change blabla.png to uuid.png, this will probably have a fit if you give it "blabla" with no ".xyz"
        filename = f"{uuid4().hex}{os.path.splitext(original_filename)[-1]}"
        
        file_path=os.path.join(self.PHOTO_UPLOAD_DIRECTORY, filename)
        
        try: 
            buff = open(file_path, "wb")
            buff.write(upload_file.file.read())
            buff.close()
            
            # throw the filepath and filename in the queue to be processed
            self.processing_queue.put((file_path,original_filename))
            
        except Exception as e:
            log_error(e)

        return file_path, original_filename


    def process_photo(self,filepath: str):
        photo = self.processing_queue.get()
        try:

            if not photo.content_type == ("image/jpeg" or "image/png" or "image/webp"):
                self._add_reject(filepath)
        except Exception as e:
            log_error(e)
    