from fastapi import FastAPI
from app.db.database import Base
from app.db.database import engine
from app.routes import expense, category, source, merchant, budget
from app.core.cors import setup_cors

app = FastAPI()

setup_cors(app)

Base.metadata.create_all(bind=engine)

app.include_router(expense.router)
app.include_router(category.router)
app.include_router(source.router)
app.include_router(merchant.router)
app.include_router(budget.router)

@app.get("/")
def home():
    return {"message": "running"}