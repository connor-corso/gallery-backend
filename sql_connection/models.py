from sqlalchemy import Column, ForeignKey, Integer, String, Boolean, Table
from sqlalchemy.orm import relationship

from .database import Base

photo_tag_association = Table("photo_tag_association", Base.metadata, 
    Column("photo_id", Integer, ForeignKey("photos.photo_id")),
    Column("tag_id", Integer, ForeignKey("tags.id"))
)

class Photo(Base):
    class Config:
        from_attributes = True
    __tablename__ = "photos"

    photo_id = Column(Integer, primary_key=True, autoincrement=True)
    photo_title = Column(String(255))
    photo_path = Column(String(255))
    thumbnail_path = Column(String(255))


    uploaded_at = Column(Integer)
    processed = Column(Boolean, default=False)

    visibility = Column(Integer)
    motion_photo = Column(Boolean, default=False)
    favorite = Column(Boolean, default=False)

    tags = relationship("Tag", secondary=photo_tag_association, back_populates="photos")


class Tag(Base):
    class Config:
        from_attributes = True
    __tablename__ = "tags"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name=Column(String, unique=True, nullable=False)
    photos = relationship("Photo", secondary=photo_tag_association, back_populates="tags")