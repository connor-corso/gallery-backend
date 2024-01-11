import os
from fastapi import UploadFile
from uuid import uuid4
import queue
from errorlogger import log_error
from sql_connection import crud
import re
import magic
import shutil
from sql_connection import schemas
from PIL import Image, ImageOps
from motionphotohandler import MotionPhotoHandler

class PhotoHandler():
    def __init__(self):
        self.processing_queue = queue.Queue()
        
        
        # setup all the picture directories by checking to see if an environment variable exists for that and if not use the default
        
        self.PHOTO_ROOT_DIRECTORY = os.getenv("PHOTO_ROOT_DIRECTORY")
        if self.PHOTO_ROOT_DIRECTORY is None:
            self.PHOTO_ROOT_DIRECTORY = "/photos"                                 ## the root folder of all the pics

        
        self.PHOTO_CACHE_DIRECTORY = os.getenv("PHOTO_CACHE_DIRECTORY")
        if self.PHOTO_CACHE_DIRECTORY is None:
            self.PHOTO_CACHE_DIRECTORY = "/photos/cache"                          ## the folder where pics will have their icons placed after being processed
        

        self.PHOTO_UPLOAD_DIRECTORY = os.getenv("PHOTO_UPLOAD_DIRECTORY")
        if self.PHOTO_UPLOAD_DIRECTORY is None:
            self.PHOTO_UPLOAD_DIRECTORY = "/photos/uploads"                       ## the folder where new pics will get uploaded before getting processed
            

        self.PHOTO_REJECTS_DIRECTORY = os.getenv("PHOTO_REJECTS_DIRECTORY")
        if self.PHOTO_REJECTS_DIRECTORY is None:
            self.PHOTO_REJECTS_DIRECTORY = "/photos/rejects"                      ## the folder where reject photos will go
            
        self.PHOTO_ORIGINALS_DIRECTORY = os.getenv("PHOTO_ORIGINALS_DIRECTORY")
        if self.PHOTO_ORIGINALS_DIRECTORY is None:
            self.PHOTO_ORIGINALS_DIRECTORY = "/photos/originals"                  ## the folder where the original photos will be moved to after being processed
            
        self.PHOTO_MOTION_PHOTOS_DIRECTORY = os.getenv("PHOTO_MOTION_PHOTOS_DIRECTORY")
        if self.PHOTO_MOTION_PHOTOS_DIRECTORY is None:
            self.PHOTO_MOTION_PHOTOS_DIRECTORY = "/photos/motion_photos"          ## the folder where the motion part of motion photos will go
            
        self.PHOTO_PROCESSED_PHOTOS_DIRECTORY = os.getenv("PHOTO_PROCESSED_PHOTOS_DIRECTORY")
        if self.PHOTO_PROCESSED_PHOTOS_DIRECTORY is None:
            self.PHOTO_PROCESSED_PHOTOS_DIRECTORY = "/photos/processed_photos"    ## the folder where processed photos will go
            

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

    # throw the reject photo into the reject pile and log it
    def _add_reject(self,photodata: schemas.Photo) -> int:
        print("adding reject photo: " + str(photodata.photo_title))
        print(f"adding reject photo: {photodata.photo_title}")
        log_error(f"file: {photodata.photo_title} ({photodata.photo_path}) was a reject")
        return 10
        
    def create_thumbnail(self, processed_filepath, thumbnail_filepath, dimension = 512, quality=85):
        """
        Create and save a compressed thumbnail of the image, this will crop the image to be exactly dimension x dimension pixels
        
        :param input_path: Path to the input image.
        :param output_path: Path to save the compressed thumbnail.
        :param max_size: The maximum size of the thumbnail's width or height.
        :param quality: The image quality, on a scale from 1 (worst) to 95 (best).
        """
        

        print(f"creating a thumbnail for {processed_filepath} and dumping it into {thumbnail_filepath}")
        
        with Image.open(processed_filepath) as img:
            ratio = dimension / (min(img.size[0],img.size[1])) 
            print(f"size[0]={img.size[0]}, size[1]={img.size[1]}, ratio={ratio}")
            img.resize((int(img.size[0] * ratio), int(img.size[1] * ratio)), Image.Resampling.LANCZOS)
            if img.mode in ("RGBA", "P", "LA", "CMYK"):
                img = img.convert("RGB")
            thumb = ImageOps.fit(img,(int(dimension),int(dimension)),Image.Resampling.BICUBIC)
            thumb.save(thumbnail_filepath, format="JPEG", quality=quality, optimize=True)
            #img.thumbnail((dimensions,dimensions))
            #img.save(thumbnail_filepath, format="JPEG", quality=quality, optimize=True)
    
    def _add_goodphoto(self,photodata: schemas.Photo,db) -> int:
        """
        Take the known good photo and store it

        Parameters:
        photodata (schemas.Photo): Takes in the photodata object

        Returns:
        0 (int): Returns 0 *should maybe return something else if it fails to copy or crud fails*
        """
        print(f"adding a good photo: {photodata.photo_title}")
        # get the name of the file
        base_filename = str(os.path.basename(photodata.photo_path))
        base_motion_photo_filename = re.sub(r'\.jpg$', '.mp4',base_filename)
        # build the processed and originals path
        processed_filepath = os.path.join(self.PHOTO_PROCESSED_PHOTOS_DIRECTORY, base_filename)
        originals_filepath = os.path.join(self.PHOTO_ORIGINALS_DIRECTORY, base_filename)
        thumbnail_filepath = os.path.join(self.PHOTO_CACHE_DIRECTORY, base_filename)
        
        # set the motion photo filepath 
        motion_photo_filepath = os.path.join(self.PHOTO_MOTION_PHOTOS_DIRECTORY,base_motion_photo_filename)
        photodata.motion_photo_path = motion_photo_filepath
        
        print(f"Thumb: {thumbnail_filepath}, processed: {processed_filepath}")
        # make a copy to the originals then move it to the processed
        shutil.copy(photodata.photo_path, originals_filepath)
        shutil.move(photodata.photo_path,  processed_filepath)
        photodata.photo_path = processed_filepath
        # create a thumbnail for faster loading times
        self.create_thumbnail(processed_filepath=processed_filepath, thumbnail_filepath=thumbnail_filepath)
        
        # check to see if it is a motion photo
        self.process_motion_photo(photodata)

        # Set the photodata's photo path and thumbnail path for later lookups
        photodata.photo_path=processed_filepath
        photodata.thumbnail_path=thumbnail_filepath
        crud.add_photo(db,photodata)
        return 0

    def _enqueue_processing(self):
        pass

    # returns 0 if the photo was accepted, 10 if the photo was a reject
    def handle_photo(self, upload_file: UploadFile, db) -> int:
        """
        This function takes an uploadfile from fastapi and does all of the behind the scenes work to save the file and add a record into the db so that you can pull the image out later

        Parameters:
        upload_file (UploadFile): The uploadfile from fastapi
        db (database): the database dependency
        
        Returns:
        int: Returns an int that signifies the outcome of handling the photo, if it was accepted returns 0, if it was added to the rejects then it returns 10
        """


        print(f"handling photo: {upload_file.filename}")
        # save the upload file to a temp file that can be thrown in the queue
        original_filename = upload_file.filename
        # change blabla.png to uuid.png, this will probably have a fit if you give it "blabla" with no ".xyz"
        filename = f"{uuid4().hex}{os.path.splitext(original_filename)[-1]}"
        
        file_path=os.path.join(self.PHOTO_UPLOAD_DIRECTORY, filename)
        
        photodata = schemas.PhotoCreate(photo_title=original_filename, photo_path=file_path, thumbnail_path=file_path,motion_photo_path=file_path, uploaded_at=0,visibility=-1,motion_photo=False,favorite=False)

        try: 
            buff = open(file_path, "wb")
            buff.write(upload_file.file.read())
            buff.close()
            
            # throw the filepath and filename in the queue to be processed
            return self.process_photo(photodata,db)
            #self.processing_queue.put((file_path,original_filename))
            
        except Exception as e:
            log_error(e)

        return file_path, original_filename


    def process_photo(self,photodata: schemas.Photo,db) -> int:
        print(f"processing photo: {photodata.photo_title}")
        #photo = self.processing_queue.get()
        try:

            # check to see if the file is an photo according to the magic numbers at the start of the file
            if is_photo(photodata.photo_path) and is_valid_filename(photodata.photo_title):
                return self._add_goodphoto(photodata,db)
            else:
                return self._add_reject(photodata)
        except Exception as e:
            log_error(e)

    
    def reprocess_photo(self, photo_info: schemas.Photo):
        print("regenerating thumbnail for: ", photo_info.photo_title)
        #print(f"removing file found at: {photo_info.thumbnail_path}")
        try:
            #shutil.rmtree(photo_info.thumbnail_path)
            os.remove(os.path.abspath(photo_info.thumbnail_path))
            #os.unlink(photo_info.thumbnail_path)
        except Exception as e:
            print(e)
        self.create_thumbnail(processed_filepath=photo_info.photo_path, thumbnail_filepath=photo_info.thumbnail_path)

    def process_motion_photo(self, photo_info: schemas.Photo):
        print("processing this file to see if it is a motion photo: ", photo_info.photo_title)
        
        # result = (photo_path,video_path) or it can be false
        result = MotionPhotoHandler.split_file(photo_info.photo_path, photo_info.motion_photo_path)

        # if the result is false then the file is not a motion photo
        if result is False:
            print("looks like it wasnt a motion photo")
            photo_info.motion_photo = False
            return
        
        # The file is a motion photo
        photo_info.motion_photo = True
        print("Looks like it was a motion photo")
        #(split_photo, split_video) = result

        # we can replace the picture that is there with this one to save some space, then copy the video into the videopath
        #shutil.copy(split_photo,photo_info.photo_path)
        #shutil.copy(split_video,photo_info.motion_photo_path)

        


        # three steps, first we need to split out the image from the video
        # then we need to call ffmpeg to reencode the video to 264
        # then we need to store the new image and video somewhere.. probably with another row in the database

        # need to call ffmpeg or something here...
        #command = ['ffmpeg', 'y', '-i', photo_info.photo_path, '-c:v', 'libx264', '-crf', '18', '-vf', 'format=yuv420p', '-c:a', 'copy', photo_info.photo_path]
    
def is_photo(file_path) -> bool:
    print(f"Checking if {file_path} is a photo")
    print("Checking if this is a photo: " + str(file_path))
    mime = magic.Magic(mime=True)
    mime_type = mime.from_file(file_path)
    status = mime_type.startswith("image/")
    print(f"Photo status: {status}")
    print("Photo status: " + str(status))
    return status
def is_valid_filename(filename: str) -> bool:
    return bool(re.match("^[a-zA-Z0-9_.-]+$", filename))