from pydantic import BaseModel
from typing import List


class CompanyNameOut(BaseModel):
    company_name: str

    class Config:
        orm_mode = True


class CompanyOut(BaseModel):
    company_name: str
    tags: List[str]

    class Config:
        orm_mode = True
