from typing import List, Optional
from pydantic import BaseModel

# Gallery Schema
class GalleryBase(BaseModel):
    gallery_title: str

class GalleryCreate(GalleryBase):
    pass

class Gallery(GalleryBase):
    gallery_id: int
    photos: List[int] = []

    class Config:
        from_attributes = True



##########

# Tag Schema
class TagBase(BaseModel):
    tag_title: str

class TagCreate(TagBase):
    pass

class Tag(TagBase):
    tag_id: int

###########

# Photo Schema
class PhotoBase(BaseModel):
    photo_title: Optional[str]

    photo_path: Optional[str]
    thumbnail_path: Optional[str]

    uploaded_at: Optional[int]
    processed: bool = False
    motion_photo: Optional[bool]
    favorite: Optional[bool]
    motion_photo_path: Optional[str]
    


class PhotoCreate(PhotoBase):
    pass

class PhotoUpdate(PhotoBase):
    pass

class Photo(PhotoBase):
    photo_id: int
    tags: List[int] = []
    galleries: List[int] = []

    class Config:
        from_attributes = True

