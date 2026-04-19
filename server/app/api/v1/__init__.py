from fastapi import APIRouter

from app.api.v1 import auth, diaries, events, modules, profile, stats

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(diaries.router, prefix="/diaries", tags=["diaries"])
api_router.include_router(events.router, prefix="/events", tags=["events"])
api_router.include_router(modules.router, prefix="/modules", tags=["modules"])
api_router.include_router(profile.router, prefix="/profile", tags=["profile"])
api_router.include_router(stats.router, prefix="/stats", tags=["stats"])
