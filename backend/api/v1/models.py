from pydantic import BaseModel
from typing import Optional, Any, List

class User(BaseModel):
    id: int
    email: str

    class Config:
        from_attributes = True

class ExtractedDataResponse(BaseModel):
    id: int
    status: int
    file_hash: str
    extracted_toon_object: Optional[Any] = None

    class Config:
        from_attributes = True

class EntityResponse(BaseModel):
    id: int
    user_id: int
    name: str
    entity_metadata: Optional[Any] = None
    doc_path: Optional[str] = None
    extracted_data: List[ExtractedDataResponse] = []

    class Config:
        from_attributes = True