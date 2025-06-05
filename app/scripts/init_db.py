# import asyncio
from app.database import Base, engine
from app.models import company
from app.database import Base

def init_models():
    with engine.begin() as conn:
        # conn.run_sync(Base.metadata.create_all)
        Base.metadata.create_all(bind=conn)

if __name__ == "__main__":
    # asyncio.run(init_models())
    init_models()
