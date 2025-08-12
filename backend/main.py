from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from app.core.config import settings
from app.core.database import engine
from app.api.v1.api import api_router
from app.core.auth import get_current_user

app = FastAPI(
    title="AgriLink API",
    description="B2B/B2C agriculture marketplace API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://frontend:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for KYC documents
app.mount("/storage", StaticFiles(directory="storage"), name="storage")

# Include API router
app.include_router(api_router, prefix="/api/v1")

# Create database tables after app is created
@app.on_event("startup")
async def startup_event():
    from sqlmodel import SQLModel
    SQLModel.metadata.create_all(bind=engine)

@app.get("/")
async def root():
    return {"message": "Welcome to AgriLink API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
