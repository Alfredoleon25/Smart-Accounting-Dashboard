from sqlalchemy import Column, Integer, String, LargeBinary, Text
from database import Base

class UploadedFile(Base):
    __tablename__ = "uploaded_files"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    content_type = Column(String)
    data = Column(LargeBinary)
    ai_summary = Column(Text)
    user_email = Column(String,index=True)
