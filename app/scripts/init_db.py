from app.database import engine, Base
from app.models import company

Base.metadata.create_all(bind=engine)
