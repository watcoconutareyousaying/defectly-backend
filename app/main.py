from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import user, activity_log, project, plan, case, requirement
from app.db.session import engine
from app.db.base import Base

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Defectly API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(user.router, prefix="/api/v1", tags=["Authentication"])
app.include_router(activity_log.router, prefix="/api/v1", tags=["Activity Logs"])
app.include_router(project.router, prefix="/api/v1/projects", tags=["Projects"])
app.include_router(plan.router, prefix="/api/v1", tags=["Test Plans"])
app.include_router(case.router, prefix="/api/v1", tags=["Test Case"])
app.include_router(requirement.router, prefix="/api/v1/requirements", tags=["Requirements"])


@app.get("/")
def read_root():
    return {"message": "Authentication API is running"}
