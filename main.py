from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import engine, Base
from routers import users, applications

# Create tables (for development — use Alembic migrations in production)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="JobPilot API",
    description="Job Application Tracker API",
    version="1.0.0",
)

# CORS — allow frontend to call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://jobpilottrack.netlify.app/"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(users.router)
app.include_router(applications.router)


@app.get("/")
def root():
    return {"message": "JobPilot API is running", "docs": "/docs"}
