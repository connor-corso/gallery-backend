from typing import List, Optional
from pydantic import BaseModel



# Tag Schema
class TagBase(BaseModel):
    name: str

class TagCreate(TagBase):
    pass

class Tag(TagBase):
    id: int

    class Config:
        orm_mode = True

###########

# Photo Schema
class PhotoBase(BaseModel):
    photo_title: Optional[str]
    photo_path: Optional[str]
    thumbnail_path: Optional[str]
    uploaded_at: Optional[int]
    processed: bool = False
    visibility: Optional[int]
    motion_photo: Optional[bool]
    favorite: Optional[bool]
    


class PhotoCreate(PhotoBase):
    pass

class PhotoUpdate(PhotoBase):
    pass

class Photo(PhotoBase):
    photo_id: int
    tags: List[Tag] = []

    class Config:
        orm_mode = True