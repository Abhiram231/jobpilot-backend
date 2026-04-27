from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import engine, Base
from routers import users, applications

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="JobPilot API",
    description="Job Application Tracker API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router)
app.include_router(applications.router)


@app.get("/")
def root():
    return {"message": "JobPilot API is running", "docs": "/docs"}
