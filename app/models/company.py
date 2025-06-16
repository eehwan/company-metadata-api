from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base

class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True)
    names = relationship("CompanyName", back_populates="company", cascade="all, delete-orphan")
    tags = relationship("CompanyTag", back_populates="company", cascade="all, delete-orphan")


class CompanyName(Base):
    __tablename__ = "company_names"

    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    language = Column(String, nullable=False)
    name = Column(String, nullable=False, index=True)

    company = relationship("Company", back_populates="names")

    __table_args__ = (UniqueConstraint("company_id", "language", name="uix_company_lang"),)


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True)
    names = relationship("TagName", back_populates="tag", cascade="all, delete-orphan")
    companies = relationship("CompanyTag", back_populates="tag", cascade="all, delete-orphan")


class TagName(Base):
    __tablename__ = "tag_names"

    id = Column(Integer, primary_key=True)
    tag_id = Column(Integer, ForeignKey("tags.id", ondelete="CASCADE"), nullable=False)
    language = Column(String, nullable=False)
    name = Column(String, nullable=False, index=True)

    tag = relationship("Tag", back_populates="names")

    __table_args__ = (UniqueConstraint("tag_id", "language", name="uix_tag_lang"),)


class CompanyTag(Base):
    __tablename__ = "company_tags"

    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), primary_key=True, nullable=False)
    tag_id = Column(Integer, ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True, nullable=False)

    company = relationship("Company", back_populates="tags")
    tag = relationship("Tag", back_populates="companies")
