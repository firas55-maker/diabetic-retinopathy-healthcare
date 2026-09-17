from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import init_db, engine
from models import Base
from routes.auth import router as auth_router
from routes.patients import router as patients_router, scans_router, lookup_router
from routes.doctor import router as doctor_router
from routes.dashboard import router as dashboard_router
from routes.chat import router as chat_router
from config import settings

# Create tables (deferred to startup to handle missing DB gracefully)
db_initialized = False

def init_database():
    global db_initialized
    if not db_initialized:
        try:
            Base.metadata.create_all(bind=engine)
            db_initialized = True
        except Exception as e:
            print(f"Warning: Could not initialize database: {e}")
            print("Database will be created when PostgreSQL is available")

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Healthcare management system API with JWT authentication and retinal scan analysis"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change this to specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(patients_router)
app.include_router(scans_router)
app.include_router(lookup_router)
app.include_router(doctor_router)
app.include_router(dashboard_router)
app.include_router(chat_router)

@app.get("/", tags=["Health"])
async def root():
    """Health check endpoint"""
    return {
        "message": "Healthcare API is running",
        "version": settings.APP_VERSION
    }

@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "app": settings.APP_NAME
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=settings.DEBUG)
