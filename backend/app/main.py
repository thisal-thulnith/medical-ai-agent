"""
Main FastAPI application
Medical AI Agent - Chat-first platform
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.core.database import Base, engine
from app.api import auth, chat, dashboard, upload

# Create database tables
Base.metadata.create_all(bind=engine)

# Create demo user
from app.models.user import User
from app.core.security import get_password_hash
from app.core.database import SessionLocal

def create_demo_user():
    """Create demo user for testing"""
    db = SessionLocal()
    try:
        demo_user = db.query(User).filter(User.email == "demo@medical.ai").first()
        if not demo_user:
            demo_user = User(
                email="demo@medical.ai",
                password_hash=get_password_hash("demo123"),
                full_name="Demo User",
            )
            db.add(demo_user)
            db.commit()
            print("✅ Demo user created: demo@medical.ai / demo123")
    finally:
        db.close()

create_demo_user()

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="AI-powered medical assistant with chat interface, symptom tracking, and health analytics",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins in development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(dashboard.router)
app.include_router(upload.router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Medical AI Agent API",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "online"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT
    }


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "error": str(exc) if settings.DEBUG else "An error occurred"
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
