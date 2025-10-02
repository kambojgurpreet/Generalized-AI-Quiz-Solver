from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import os
from dotenv import load_dotenv

from app.api.routes import router
from app.services.redis_service import RedisService

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="AI Quiz Solver API",
    description="Backend API for AI-powered quiz solving",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix="/api")

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    try:
        # Initialize Redis connection
        redis_service = RedisService()
        await redis_service.ping()
        print("✅ Redis connection established")
    except Exception as e:
        print(f"⚠️ Redis connection failed: {e}")
        print("⚠️ Running without Redis - caching disabled")
        print("💡 To enable caching, install Redis or use Docker setup")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    try:
        redis_service = RedisService()
        await redis_service.close()
        print("✅ Redis connection closed")
    except Exception as e:
        print(f"⚠️ Error closing Redis connection: {e}")

@app.get("/")
async def root():
    return {"message": "AI Quiz Solver API", "status": "running"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        redis_service = RedisService()
        redis_status = await redis_service.ping()
        return {
            "status": "healthy",
            "redis": "connected" if redis_status else "disconnected"
        }
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "error": str(e)}
        )

if __name__ == "__main__":
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", 8000))
    debug = os.getenv("DEBUG", "False").lower() == "true"
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=debug
    )