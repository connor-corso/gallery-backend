import subprocess
import os
import re
from typing import BinaryIO

class MotionPhotoHandler():
    # will return a tuple (photo,video) if it is a motion photo, false otherwise
    # this will have a fit if we try to do multiple splits at once
    def split_file(inputfile: str, final_video_path):
        print("splitfile")
        
        # get the splitpoint
        splitpoint = MotionPhotoHandler._get_file_data(inputfile)
        
        if splitpoint == 0 or splitpoint == False:
            return False
        
        tempvideo = "video.mp4"
        tempphoto = "photo.jpg"
        
        
        try:
            print("open files")
            videofile: BinaryIO
            inputfile: BinaryIO
            #photofile: BinaryIO

            try: 
                videofile = open(tempvideo, 'x+b')
            except FileExistsError as e:
                print("file exists, it should be open anyways")
                print(e)
            
            
            try: 
                inputfile = open(inputfile, 'r+b')
                inputfile.seek(0)
            except FileExistsError as e:
                print("file exists, it should be open anyways")
                print(e)
            
            #try: 
            #    photofile = open(tempphoto, 'xb')
            #except FileExistsError as e:
            #    print("file exists, it should be open anyways")
            #    print(e)

            print("opened files")

            # copy over the photo portion of the file
            #photoportion = inputfile.read(splitpoint)
            #photofile.write(photoportion)
            
            # skip to the video portion of the mixed file
            inputfile.seek(splitpoint)

            # copy over the video portion of the file
            videoportion = inputfile.read()
            videofile.write(videoportion)

            # truncate the input file to remove the video portion
            inputfile.seek(0)
            inputfile.truncate(splitpoint)
            #photofile.seek(0)
            #inputfile.seek(0)
            #inputfile.truncate(0)
            #inputfile.write(photofile)

            videofile.close()
            #photofile.close()
            inputfile.close()

            MotionPhotoHandler._transcode_video(tempvideo, final_video_path)
            os.remove(videofile)
            

            
        except Exception as e:
            print("error splitting the video and photo")
            print(e)
            return False
        
        return True
    
    def _transcode_video(inputfile, outputfile):
        print("transcode")
        command = ['ffmpeg', '-y', '-i', inputfile, '-c:v', 'libx264', '-crf', '25', '-vf', 'format=yuv420p', '-c:a', 'copy', outputfile]
        subprocess.run(command)


    def _get_file_size(inputfile):
        print("getfilesize")
        return os.path.getsize(inputfile)
    
    # returns the splitpoint, the point that the file can be split at to separate out the picture and the video
    def _get_file_data(inputfile):
        print("getfiledata")
        try:
            f = open(inputfile, "rb")
            filedata = f.read()

            filesize = MotionPhotoHandler._get_file_size(inputfile)
            print(f"filesize: {filesize}")
            # pull out the xmpmetadata from the photo
            xmp_start = filedata.find(b'<x:xmpmeta')
            xmp_end = filedata.find(b'</x:xmpmeta')
            xmp_bytes = filedata[xmp_start: xmp_end + 12]
        
            f.close()

            xmp_str = str(xmp_bytes)

            # pull out the "length=number in the xmp metadata"
            lengthlist = re.findall("Length=\"[^\"]*\"", xmp_str)
            # now we just want the numbers. I could probably make this work in one regex but this is known to work.. dont fix it if it isnt broken
            numberslist= re.findall(r'\d+', ('\n'.join(lengthlist)))
            print('\n'.join(lengthlist))

            # check to see if the file is a motion photo by seeing if there were any length matches
            if len(numberslist) == 0:
                return False
            
            # find the biggest of the two numbers
            splitpoint = 0
            for number in numberslist:
                if int(number) > splitpoint and int(number) < filesize:
                    splitpoint = int(number)

            # since the splitpoint tells you the size of the video, and the photo comes before the video in the file then we know the photo is filesize-splitpoint bytes
            splitpoint = filesize - splitpoint

            return splitpoint
        

        except Exception as e:
            print("there was an error looking into the file to split it into a motion photo")
            print(e)

        return False
