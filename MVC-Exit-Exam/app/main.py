from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from app.controllers.views import router as views_router
from app.controllers.api import router as api_router

app = FastAPI(title="CS Crowdfund (MVC)")

app.add_middleware(SessionMiddleware, secret_key="DSvUNKdu62uaU8l9UPpNUFW-OKGfsP7tMoRyqmN6QvE")

app.include_router(views_router)

app.include_router(api_router, prefix="/api")

@app.get("/health")
def health():
    return {"ok": True}
