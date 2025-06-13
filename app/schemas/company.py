from pydantic import BaseModel, Field
from typing import Dict, List

class TagNameIn(BaseModel):
    tag_name: Dict[str, str]

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "tag_name": {"ko": "태그_1", "en": "tag_1", "ja": "タグ_1"}
                },
            ]
        }
    }

class CompanyCreateIn(BaseModel):
    company_name: Dict[str, str]
    tags: List[TagNameIn]

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "company_name": {"ko": "원티드랩", "en": "Wantedlab", "ja": "ウォンテッドラボ"},
                "tags": [
                    {"tag_name": {"ko": "태그_1", "en": "tag_1", "ja": "タグ_1"}},
                    {"tag_name": {"ko": "태그_2", "en": "tag_2", "ja": "タグ_2"}}
                ]
            }]
        }
    }

class CompanyNameOut(BaseModel):
    company_name: str

    class Config:
        orm_mode = True


class CompanyOut(BaseModel):
    company_name: str
    tags: List[str]

    class Config:
        orm_mode = True
