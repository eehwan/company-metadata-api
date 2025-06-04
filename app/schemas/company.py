from typing import List
from pydantic import BaseModel


class CompanyNameOut(BaseModel):
    language: str
    name: str

    class Config:
        orm_mode = True


class TagNameOut(BaseModel):
    language: str
    name: str

    class Config:
        orm_mode = True


class TagOut(BaseModel):
    # id: int
    names: List[TagNameOut]

    class Config:
        orm_mode = True


class CompanyTagOut(BaseModel):
    tag: TagOut

    class Config:
        orm_mode = True


class CompanyOut(BaseModel):
    id: int
    names: List[CompanyNameOut]
    tags: List[CompanyTagOut]

    class Config:
        orm_mode = True
