from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.contact import router as contact_router

app = FastAPI(
    title="Codeflux API",
    description="Backend API for Codeflux",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://codeflux.com.au",
        "https://www.codeflux.com.au",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {
        "message": "Welcome to Codeflux API"
    }


@app.get("/api/health")
async def health():
    return {
        "status": "healthy"
    }

app.include_router(contact_router)