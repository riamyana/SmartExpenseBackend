from fastapi import FastAPI
from app.core.database import Base
from app.core.database import engine
from app.routes import auth, expense, category, source, merchant, budget
from app.core.cors import setup_cors

app = FastAPI()

setup_cors(app)

Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(expense.router)
app.include_router(category.router)
app.include_router(source.router)
app.include_router(merchant.router)
app.include_router(budget.router)

@app.get("/")
def home():
    return {"message": "running"}