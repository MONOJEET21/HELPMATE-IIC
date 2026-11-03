from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.database import Base, engine
from app import models
from app.routers import auth, jobs, farms, sensors, ai, marketplace, workers

Base.metadata.create_all(bind=engine)
app = FastAPI(title="HelpMate² API", version="1.0.0",
              description="Parent platform APIs for HelpMate Jobs and AgriBrain.")
app.add_middleware(CORSMiddleware, allow_origins=[settings.frontend_origin],
                   allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
for r in [auth.router, jobs.router, farms.router, sensors.router, ai.router, marketplace.router, workers.router]:
    app.include_router(r)

@app.get("/")
def root():
    return {"name":"HelpMate² API","status":"running","docs":"/docs"}
@app.get("/api/health")
def health():
    return {"status":"healthy"}
