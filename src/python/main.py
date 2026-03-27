from fastapi import FastAPI
from database import Base
from database import engine
from routes import expense

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(expense.router)

@app.get("/")
def home():
    return {"message": "running"}