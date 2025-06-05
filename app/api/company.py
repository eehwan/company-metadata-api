from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.database import get_session
from app.schemas.company import CompanyOut, CompanyNameOut
from app.crud import company as crud

router = APIRouter(tags=["companies"])


@router.get("/search", response_model=List[CompanyNameOut])
def search_company_name(
    query: str,
    x_wanted_language: Optional[str] = Header(default="ko"),
    db: AsyncSession = Depends(get_session)
):
    return crud.autocomplete_company_name(db, query, x_wanted_language)


@router.get("/companies/{company_name}", response_model=CompanyOut)
def get_company_by_name(
    company_name: str,
    x_wanted_language: Optional[str] = Header(default="ko"),
    db: AsyncSession = Depends(get_session)
):
    company = crud.get_company_by_name(db, company_name, x_wanted_language)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company


@router.get("/tags", response_model=List[CompanyNameOut])
def search_by_tag(
    query: str,
    x_wanted_language: Optional[str] = Header(default="ko"),
    db: AsyncSession = Depends(get_session),
):
    return crud.search_companies_by_tag_name(db, query, x_wanted_language)


@router.put("/companies/{company_name}/tags", response_model=CompanyOut)
def add_tag_to_company(
    company_name: str,
    tags: List[dict],
    x_wanted_language: Optional[str] = Header(default="ko"),
    db: AsyncSession = Depends(get_session),
):
    company_id = crud.get_company_id_by_name(db, company_name)
    if not company_id:
        raise HTTPException(status_code=404, detail="Company not found")

    for tag_entry in tags:
        tag_name_dict = tag_entry.get("tag_name", {})
        tag_id = crud.get_or_create_tag(db, tag_name_dict)
        crud.add_company_tag_relation(db, company_id, tag_id)

    return crud.get_company_name_and_tags(db, company_id, x_wanted_language)


@router.post("/companies", response_model=CompanyOut)
def create_company(
    body: dict,
    x_wanted_language: Optional[str] = Header(default="ko"),
    db: AsyncSession = Depends(get_session),
):
    company_id = crud.create_company(db, body, x_wanted_language)
    return crud.get_company_name_and_tags(db, company_id, x_wanted_language)


@router.delete("/companies/{company_name}/tags/{tag_name}", response_model=CompanyOut)
def remove_tag_from_company(
    company_name: str,
    tag_name: str,
    x_wanted_language: Optional[str] = Header(default="ko"),
    db: AsyncSession = Depends(get_session),
):
    company_id = crud.get_company_id_by_name(db, company_name)
    if not company_id:
        raise HTTPException(status_code=404, detail="Company not found")

    crud.delete_company_tag_by_name(db, company_id, tag_name)
    return crud.get_company_name_and_tags(db, company_id, x_wanted_language)
