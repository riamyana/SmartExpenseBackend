from fastapi import FastAPI
from app.database import Base
from app.database import engine
from app.routes import expense, category, source, merchant

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(expense.router)
app.include_router(category.router)
app.include_router(source.router)
app.include_router(merchant.router)

@app.get("/")
def home():
    return {"message": "running"}