from fastapi import APIRouter, HTTPException
from app.models import repo_csv as repo

router = APIRouter(tags=["api"])

@router.get("/projects")
def api_projects():
    return [vars(p) for p in repo.list_projects()]

@router.get("/projects/{pid}")
def api_project(pid: str):
    p = repo.get_project(pid)
    if not p:
        raise HTTPException(404, "Project not found")
    return vars(p)