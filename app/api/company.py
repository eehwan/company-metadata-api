from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_async_session
from app.crud.company import get_all_companies, autocomplete_company_names, search_companies, search_companies_by_name, search_companies_by_tag_name
from app.schemas.company import CompanyOut
from app.utils.language import get_preferred_language

router = APIRouter(prefix="/companies", tags=["companies"])

@router.get("/", response_model=list[CompanyOut])
async def read_companies(db: AsyncSession = Depends(get_async_session), language: str = Depends(get_preferred_language)):
    return await get_all_companies(db=db, language=language)

@router.get("/autocomplete", response_model=list[str])
async def autocomplete_companies(query: str = Query(..., min_length=1), db: AsyncSession = Depends(get_async_session)):
    return await autocomplete_company_names(query=query, db=db)

@router.get("/search", response_model=list[CompanyOut])
async def search(query: str = Query(..., min_length=1), db: AsyncSession = Depends(get_async_session), language: str = Depends(get_preferred_language)):
    return await search_companies(query=query, db=db, language=language)

@router.get("/search_by_name", response_model=list[CompanyOut])
async def search_by_company_name(query: str = Query(..., min_length=1), db: AsyncSession = Depends(get_async_session), language: str = Depends(get_preferred_language)):
    return await search_companies_by_name(query=query, db=db, language=language)

@router.get("/search_by_tag", response_model=list[CompanyOut])
async def search_by_tag_name(query: str = Query(..., min_length=1), db: AsyncSession = Depends(get_async_session), language: str = Depends(get_preferred_language)):
    return await search_companies_by_tag_name(query=query, db=db, language=language)