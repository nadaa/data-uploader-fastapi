from sqlalchemy import Column,String,Integer, TIMESTAMP, func

from .database import Base



# Model represents file metadata in the database
class File(Base):
    __tablename__="files"
    id = Column(Integer,primary_key=True,nullable=False)
    filename = Column(String,nullable=False)
    size = Column(Integer,nullable=False)
    num_rows = Column(Integer,nullable=False)    
    num_cols = Column(Integer,nullable=False)
    created_at = Column(TIMESTAMP(timezone=True),nullable=False,server_default=func.now())

