import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import recommendation
from app.config import get_settings
from app.config.environment import load_env_file

load_env_file()

settings = get_settings()

app = FastAPI(
    title="Similar Product Recommendation Service",
    description="API for recommending similar products to users",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(recommendation.router, tags=["recommendations"])


@app.get("/", tags=["status"])
async def root():
    """Health check endpoint"""
    return {
        "status": "ok", 
        "service": "Similar Product Recommendation Service",
        "environment": os.getenv("APP_ENV", "development")
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True
    )