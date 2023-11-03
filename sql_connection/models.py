from sqlalchemy import Column, ForeignKey, Integer, String, Boolean, Table
from sqlalchemy.orm import relationship

from .database import Base

image_tag_association = Table("image_tag_association", Base.metadata, 
    Column("image_id", Integer, ForeignKey("images.id")),
    Column("tag_id", Integer, ForeignKey("tags.id"))
)

class Photo(Base):
    __tablename__ = "images"

    image_id = Column(Integer, primary_key=True, autoincrement=True)
    image_title= Column(String(255))
    image_path = Column(String(255))
    thumbnail_path = Column(String(255))


    uploaded_at = Column(Integer)
    processed = Column(Boolean, default=False)

    visibility = Column(Integer)
    motion_photo = Column(Boolean, default=False)
    favorite = Column(Boolean, default=False)

    tags = relationship("Tag", secondary=image_tag_association, back_populates="images")


class Tag(Base):
    __tablename__ = "tags"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name=Column(String, unique=True, nullable=False)
    images = relationship("Photo", secondary=image_tag_association, back_populates="tags")