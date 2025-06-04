from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI!"}

# from fastapi import FastAPI
# from app.api import company

# app = FastAPI()
# app.include_router(company.router)