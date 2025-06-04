from fastapi import Depends
from sqlalchemy import select, or_, and_, func
from sqlalchemy.orm import selectinload, joinedload, with_loader_criteria
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.company import Company, CompanyName, CompanyTag, Tag, TagName

# 전체 회사 조회
async def get_all_companies(db: AsyncSession, language: str):
    stmt = (
        select(Company)
        .options(
            joinedload(Company.names),
            selectinload(Company.tags)
                .joinedload(CompanyTag.tag)
                .joinedload(Tag.names),
            with_loader_criteria(TagName, TagName.language == language)
        )
    )
    result = await db.execute(stmt)
    return result.scalars().unique().all()

# 검색어(회사명) 자동완성
async def autocomplete_company_names(query: str, db: AsyncSession):
    stmt = (
        select(func.distinct(CompanyName.name))
        .where(
            CompanyName.name.ilike(f"%{query}%")
        )
        .limit(10)
    )
    result = await db.execute(stmt)
    return result.scalars().all()

# 통합 검색
async def search_companies(query: str, db: AsyncSession, language: str):
    stmt_company_name = (
        select(Company.id)
        .join(Company.names)
        .where(CompanyName.name.ilike(f"%{query}%"))
    )

    stmt_tag_name = (
        select(Company.id)
        .join(Company.tags)
        .join(CompanyTag.tag)
        .join(Tag.names)
        .where(
            func.lower(TagName.name) == query.lower(),
            TagName.language == language
        )
    )

    result_name = await db.execute(stmt_company_name)
    result_tag = await db.execute(stmt_tag_name)

    company_ids = set(id for (id,) in result_name.all() + result_tag.all())
    if not company_ids:
        return []

    stmt = (
        select(Company)
        .options(
            joinedload(Company.names),
            joinedload(Company.tags)
                .joinedload(CompanyTag.tag)
                .joinedload(Tag.names),
            with_loader_criteria(TagName, TagName.language == language)
        )
        .where(Company.id.in_(company_ids))
    )
    result = await db.execute(stmt)
    companies = result.scalars().unique().all()
    return companies

# 회사명으로 검색
async def search_companies_by_name(query: str, db: AsyncSession, language: str):
    stmt = (
        select(Company)
        .join(Company.names)
        .where(CompanyName.name.ilike(f"%{query}%"))
        .options(
            joinedload(Company.names),
            selectinload(Company.tags)
                .joinedload(CompanyTag.tag)
                .joinedload(Tag.names),
            with_loader_criteria(TagName, TagName.language == language)
        )
    )
    result = await db.execute(stmt)
    return result.scalars().unique().all()


# 태그명으로 검색
async def search_companies_by_tag_name(query: str, db: AsyncSession, language: str):
    stmt = (
        select(Company)
        .join(Company.tags)
        .join(CompanyTag.tag)
        .join(Tag.names)
        .where(func.lower(TagName.name) == query.lower())
        .options(
            joinedload(Company.names),
            selectinload(Company.tags)
                .joinedload(CompanyTag.tag)
                .joinedload(Tag.names),
            with_loader_criteria(TagName, TagName.language == language)
        )
    )
    result = await db.execute(stmt)
    return result.scalars().unique().all()