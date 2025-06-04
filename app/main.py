from fastapi import FastAPI
from app.api import company

app = FastAPI()
app.include_router(company.router)