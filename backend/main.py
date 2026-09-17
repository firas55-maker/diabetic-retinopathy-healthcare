from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
import os
from database import init_db, engine
from models import Base
from routes.auth import router as auth_router
from routes.patients import router as patients_router, scans_router, lookup_router
from routes.doctor import router as doctor_router
from routes.dashboard import router as dashboard_router
from routes.chat import router as chat_router
from routes.migration import router as migration_router
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

# Include routers (API routes must come before static file serving)
app.include_router(auth_router)
app.include_router(patients_router)
app.include_router(scans_router)
app.include_router(lookup_router)
app.include_router(doctor_router)
app.include_router(dashboard_router)
app.include_router(chat_router)
app.include_router(migration_router)

@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "app": settings.APP_NAME
    }

# Mount static files for React production build
frontend_build_path = Path(__file__).parent.parent / "frontend" / "build"

if frontend_build_path.exists():
    app.mount(
        "/static",
        StaticFiles(directory=str(frontend_build_path / "static")),
        name="static"
    )

    @app.get("/{full_path:path}", include_in_schema=False)
    async def catch_all(full_path: str):
        """
        Catch-all route for React Router client-side routing.
        Serves index.html for any non-API path, allowing React Router to handle routing.
        This enables direct navigation and page refresh without 404 errors.
        """
        # List of API prefixes that should not be caught by this route
        api_prefixes = ["api", "auth", "patients", "scans", "doctor", "dashboard", "chat", "health"]

        # Check if the path starts with any API prefix
        path_parts = full_path.split("/")
        if path_parts and path_parts[0] in api_prefixes:
            # Let the API routers handle this (will 404 if not matched)
            return {"error": "Not found"}

        # Serve index.html for client-side routing
        index_path = frontend_build_path / "index.html"
        if index_path.exists():
            return FileResponse(str(index_path))
        else:
            return {"error": "Frontend build not found"}
else:
    print(f"Warning: Frontend build directory not found at {frontend_build_path}")
    print("Static files will not be served. Build the frontend with 'npm run build' in the frontend directory.")

    @app.get("/", tags=["Health"])
    async def root():
        """Health check endpoint"""
        return {
            "message": "Healthcare API is running",
            "version": settings.APP_VERSION,
            "note": "Frontend build not found - serve React app separately or build it first"
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=settings.DEBUG)
