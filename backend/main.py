from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api.interview import router as interview_router
from backend.config import settings

app = FastAPI(
    title="AI Technical Interview Agent API",
    description="Adaptive AI Interviewer API for ABTalks Hackathon",
    version="1.0.0"
)

frontend_origins = [origin.strip() for origin in settings.FRONTEND_ORIGINS.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=frontend_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(interview_router, prefix="/api")

@app.get("/health")
async def health_check():
    return {"status": "ok", "app": "AI Technical Interview Agent"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host=settings.HOST, port=settings.PORT, reload=True)
