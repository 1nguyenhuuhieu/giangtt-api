from fastapi import FastAPI
from database import db

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    db.connect()

@app.on_event("shutdown")
async def shutdown_event():
    db.disconnect()

@app.get("/")
async def read_root():
    # Example query to test the database connection
    result = db.execute("SELECT version();")
    return {"message": "FastAPI with PostgreSQL", "database_version": result[0][0]}
