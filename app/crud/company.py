from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, join
from sqlalchemy.orm import selectinload, aliased
from typing import List, Optional

from app.models.company import Company, CompanyName, CompanyTag, Tag, TagName
from app.schemas.company import CompanyNameOut


def autocomplete_company_name(db: AsyncSession, query: str, lang: str) -> List[CompanyNameOut]:
    result = db.execute(
        select(Company)
        .join(Company.names)
        .where(CompanyName.name.ilike(f"%{query}%"))
        .options(selectinload(Company.names))
    )
    companies = result.scalars().unique().all()

    name_outputs = []
    for company in companies:
        rep_name = next((n.name for n in company.names if n.language == lang), None)
        if not rep_name:
            rep_name = next((n.name for n in company.names), None)
        if rep_name:
            name_outputs.append(CompanyNameOut(company_name=rep_name))

    return name_outputs


def get_company_by_name(db: AsyncSession, name: str, lang: str):
    result = db.execute(
        select(Company)
        .join(Company.names)
        .where(CompanyName.name == name)
        .options(
            selectinload(Company.names),
            selectinload(Company.tags)
            .selectinload(CompanyTag.tag)
            .selectinload(Tag.names)
        )
    )
    company = result.scalars().first()
    if not company:
        return None

    rep_name = next((n.name for n in company.names if n.language == lang), None)
    if not rep_name:
        rep_name = next((n.name for n in company.names), "")

    tag_names = []
    for ct in company.tags:
        tag_name = next((tn.name for tn in ct.tag.names if tn.language == lang), None)
        if not tag_name:
            tag_name = next((tn.name for tn in ct.tag.names), None)
        if tag_name:
            tag_names.append(tag_name)
    
    return {
        "company_name": rep_name,
        "tags": sorted(set(tag_names), key=lambda x: int(x.split("_")[-1]))
    }


def search_companies_by_tag_name(db: AsyncSession, tag_name: str, lang: str) -> List[CompanyNameOut]:
    result = db.execute(
        select(Tag)
        .join(Tag.names)
        .where(TagName.name == tag_name)
        .options(
            selectinload(Tag.companies)
            .selectinload(CompanyTag.company)
            .selectinload(Company.names)
        )
    )
    tag = result.scalars().first()
    if not tag:
        return []

    companies = []
    for ct in tag.companies:
        company = ct.company
        rep_name = next((n.name for n in company.names if n.language == lang), None)
        if not rep_name:
            rep_name = next((n.name for n in company.names), None)
        if rep_name:
            companies.append(CompanyNameOut(company_name=rep_name))

    return companies



def get_company_id_by_name(db: AsyncSession, name: str) -> Optional[int]:
    result = db.execute(
        select(Company).join(Company.names).where(CompanyName.name == name)
    )
    company = result.scalars().first()
    return company.id if company else None


def get_or_create_tag(db: AsyncSession, tag_name_dict: dict, commit: bool = True) -> Optional[int]:
    existing_tag = None
    for lang_code, name in tag_name_dict.items():
        result = db.execute(
            select(Tag)
            .join(Tag.names)
            .where(TagName.name == name, TagName.language == lang_code)
            .options(selectinload(Tag.names))
        )
        existing_tag = result.scalars().first()
        if existing_tag:
            break

    if not existing_tag:
        new_tag = Tag()
        db.add(new_tag)
        db.flush()
        for lang_code, name in tag_name_dict.items():
            db.add(TagName(tag_id=new_tag.id, name=name, language=lang_code))
        if commit:
            db.commit()
        return new_tag.id

    existing_langs = {tn.language for tn in existing_tag.names}
    added = False
    for lang_code, name in tag_name_dict.items():
        if lang_code not in existing_langs:
            db.add(TagName(tag_id=existing_tag.id, name=name, language=lang_code))
            added = True

    if added and commit:
        db.commit()

    return existing_tag.id
    


def create_company(db: AsyncSession, body: dict, lang: str) -> Optional[int]:
    company_name_data = body["company_name"]
    tag_list = body["tags"]

    company = Company()
    db.add(company)
    db.flush()

    for lang, name in company_name_data.items():
        db.add(CompanyName(name=name, language=lang, company_id=company.id))

    for tag_dict in tag_list:
        tag_name_data = tag_dict["tag_name"]
        tag_id = get_or_create_tag(db, tag_name_data, commit=False)
        db.add(CompanyTag(company_id=company.id, tag_id=tag_id))

    db.commit()
    return company.id

def add_company_tag_relation(db: AsyncSession, company_id: int, tag_id: int):
    result = db.execute(
        select(CompanyTag).where(CompanyTag.company_id == company_id, CompanyTag.tag_id == tag_id)
    )
    if not result.scalar():
        db.add(CompanyTag(company_id=company_id, tag_id=tag_id))
        db.commit()


def delete_company_tag_by_name(db: AsyncSession, company_id: int, tag_name: str):
    tag_result = db.execute(
        select(Tag).join(Tag.names).where(TagName.name == tag_name)
    )
    tag = tag_result.scalars().first()
    if not tag:
        return

    db.execute(
        delete(CompanyTag)
        .where(CompanyTag.company_id == company_id)
        .where(CompanyTag.tag_id == tag.id)
    )
    db.commit()


def get_company_name_and_tags(db: AsyncSession, company_id: int, lang: str):
    result = db.execute(
        select(Company)
        .where(Company.id == company_id)
        .options(
            selectinload(Company.names),
            selectinload(Company.tags).selectinload(CompanyTag.tag).selectinload(Tag.names)
        )
    )
    company = result.scalars().first()
    if not company:
        return None

    name = next((n.name for n in company.names if n.language == lang), None)
    if not name:
        name = next((n.name for n in company.names), "")

    tag_names = []
    for ct in company.tags:
        tag_name = next((n.name for n in ct.tag.names if n.language == lang), None)
        if not tag_name:
            tag_name = next((n.name for n in ct.tag.names), None)
        if tag_name:
            tag_names.append(tag_name)


    return {
        "company_name": name,
        "tags": sorted(set(tag_names), key=lambda x: int(x.split("_")[-1]))
    }
