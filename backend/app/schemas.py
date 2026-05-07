from pydantic import BaseModel
from typing import List

class EmailRequest(BaseModel):
    email: str

class BatchRequest(BaseModel):
    emails: List[str]