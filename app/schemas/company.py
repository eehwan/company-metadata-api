from pydantic import BaseModel, Field
from typing import Dict, List

class TagNameIn(BaseModel):
    tag_name: Dict[str, str]


class CompanyCreateIn(BaseModel):
    company_name: Dict[str, str]
    tags: List[TagNameIn]


class CompanyNameOut(BaseModel):
    company_name: str

    model_config = {
        "from_attributes": True,
    }


class CompanyOut(BaseModel):
    company_name: str
    tags: List[str]

    model_config = {
        "from_attributes": True,
    }
