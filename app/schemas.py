from pydantic import BaseModel
from datetime import datetime

class DocumentBase(BaseModel):
    filename: str
    upload_date: datetime

class DocumentCreate(DocumentBase):
    file_path: str

class DocumentResponse(DocumentBase):
    id: int

    class Config:
        orm_mode = True
