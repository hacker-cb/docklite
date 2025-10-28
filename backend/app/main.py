from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
from app.api import projects, presets, deployment, auth, users, containers
from app.core.config import settings
from app.core.database import engine, Base

app = FastAPI(
    title="DockLite",
    description="Web Server Management System",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В production заменить на конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api")  # Auth endpoints (public)
app.include_router(users.router, prefix="/api")  # User management (admin only)
app.include_router(projects.router, prefix="/api")
app.include_router(presets.router, prefix="/api")
app.include_router(deployment.router, prefix="/api")
app.include_router(containers.router, prefix="/api/containers")  # Container management


# Startup event
@app.on_event("startup")
async def startup():
    """Initialize database and create tables"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Ensure projects directory exists
    projects_dir = Path(settings.PROJECTS_DIR)
    projects_dir.mkdir(parents=True, exist_ok=True)


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "ok",
        "message": "DockLite API is running",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


# Static files for frontend (will be uncommented when frontend is ready)
# frontend_path = Path(__file__).parent.parent.parent / "frontend" / "dist"
# if frontend_path.exists():
#     app.mount("/assets", StaticFiles(directory=str(frontend_path / "assets")), name="assets")
#     
#     @app.get("/{full_path:path}")
#     async def serve_frontend(full_path: str):
#         index_file = frontend_path / "index.html"
#         if index_file.exists():
#             return FileResponse(index_file)
#         return {"error": "Frontend not found"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=True
    )

