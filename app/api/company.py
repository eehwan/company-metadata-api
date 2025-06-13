from fastapi import APIRouter, Depends, HTTPException, Header, Body, Path, Query
# from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from typing import List, Optional, Annotated

from app.database import get_session
from app.schemas.company import TagNameIn, CompanyCreateIn, CompanyOut, CompanyNameOut
from app.crud import company as crud

router = APIRouter(tags=["companies"])


@router.get("/search", response_model=List[CompanyNameOut])
def search_company_name(
    query: Annotated[str, Query(
        min_length=1,
        max_length=20,
        description="회사명 포함 검색어",
        example="크"
    )],
    x_wanted_language: Optional[str] = Header(default="ko"),
    db: Session = Depends(get_session)
):
    return crud.autocomplete_company_name(db, query, x_wanted_language)


@router.get("/companies/{company_name}", response_model=CompanyOut)
def get_company_by_name(
    company_name: Annotated[str, Path(
        min_length=1,
        max_length=20,
        description="회사명 검색어",
        example="원티드랩"
    )],
    x_wanted_language: Optional[str] = Header(default="ko"),
    db: Session = Depends(get_session)
):
    company = crud.get_company_by_name(db, company_name, x_wanted_language)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company


@router.get("/tags", response_model=List[CompanyNameOut])
def search_by_tag(
    tag_name: Annotated[str, Query(
        min_length=1,
        max_length=20,
        description="태그명 검색어",
        example="태그_1"
    )],
    x_wanted_language: Optional[str] = Header(default="ko"),
    db: Session = Depends(get_session),
):
    return crud.search_companies_by_tag_name(db, tag_name, x_wanted_language)


@router.put("/companies/{company_name}/tags", response_model=CompanyOut)
def add_tag_to_company(
    company_name: Annotated[str, Path(
        min_length=1,
        max_length=20,
        description="대상 회사명",
        example="원티드랩"
    )],
    tags: Annotated[
        List[TagNameIn],
        Body(
            openapi_examples={
                "add_single_tag": {
                    "summary": "단일 태그 추가 예시",
                    "description": "회사에 새로운 태그 하나를 추가하는 요청입니다.",
                    "value": [
                        {"tag_name": {"ko": "태그_1", "en": "tag_1", "ja": "タグ_1"}}
                    ],
                },
                "add_multiple_tags": {
                    "summary": "복수 태그 추가 예시",
                    "description": "회사에 여러 태그를 동시에 추가하는 요청입니다.",
                    "value": [
                        {"tag_name": {"ko": "태그_1", "en": "tag_1", "ja": "タグ_1"}},
                        {"tag_name": {"ko": "태그_2", "en": "tag_2", "ja": "タグ_2"}}
                    ],
                },
            }
        )
    ],
    x_wanted_language: Optional[str] = Header(default="ko"),
    db: Session = Depends(get_session),
):
    company_id = crud.get_company_id_by_name(db, company_name)
    if not company_id:
        raise HTTPException(status_code=404, detail="Company not found")

    for tag_entry in tags:
        tag_name_dict = tag_entry.tag_name
        tag_id = crud.get_or_create_tag(db, tag_name_dict)
        crud.add_company_tag_relation(db, company_id, tag_id)

    return crud.get_company_name_and_tags(db, company_id, x_wanted_language)


@router.post("/companies", response_model=CompanyOut)
def create_company(
    body: Annotated[
        CompanyCreateIn,
        Body(
            openapi_examples={
                "create_new_company": {
                    "summary": "새로운 회사 생성 예시",
                    "description": "회사명과 여러 태그를 포함하여 새로운 회사를 생성합니다.",
                    "value": {
                        "company_name": {"ko": "새로운회사", "en": "NewCompany", "ja": "新しい会社"},
                        "tags": [
                            {"tag_name": {"ko": "태그_1", "en": "tag_1", "ja": "タグ_1"}},
                            {"tag_name": {"ko": "태그_2", "en": "tag_2", "ja": "タグ_2"}}
                        ]
                    },
                },
            }
        )
    ],
    x_wanted_language: Optional[str] = Header(default="ko"),
    db: Session = Depends(get_session),
):
    company_id = crud.create_company(db, body, x_wanted_language)
    return crud.get_company_name_and_tags(db, company_id, x_wanted_language)


@router.delete("/companies/{company_name}/tags/{tag_name}", response_model=CompanyOut)
def remove_tag_from_company(
    company_name: Annotated[str, Path(
        min_length=1,
        max_length=20,
        description="대상 회사명",
        example="원티드랩"
    )],
    tag_name: Annotated[str, Path(
        min_length=1,
        max_length=20,
        description="삭제할 태그명",
        example="태그_1"
    )],
    x_wanted_language: Optional[str] = Header(default="ko"),
    db: Session = Depends(get_session),
):
    company_id = crud.get_company_id_by_name(db, company_name)
    if not company_id:
        raise HTTPException(status_code=404, detail="Company not found")

    crud.delete_company_tag_by_name(db, company_id, tag_name)
    return crud.get_company_name_and_tags(db, company_id, x_wanted_language)
