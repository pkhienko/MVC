from datetime import date
from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.status import HTTP_303_SEE_OTHER

from app.models import repo_csv as repo
from app.models.domain_services import create_pledge

router = APIRouter()
templates = Jinja2Templates(directory="templates")

# ---------- Jinja filters ----------
def money(n):
    try:
        return f"{int(n):,}"
    except Exception:
        return str(n)

def abbr(n):
    try:
        n = float(n)
    except Exception:
        return str(n)
    for unit, div in (("T", 1e12), ("B", 1e9), ("M", 1e6), ("K", 1e3)):
        if abs(n) >= div:
            return f"{n/div:.2f}{unit}"
    return f"{n:.0f}"

def fmtdate(d):
    try:
        return d.strftime("%Y-%m-%d")
    except Exception:
        return str(d)

def fmtdt(dt):
    try:
        return dt.strftime("%Y-%m-%d %H:%M")
    except Exception:
        return str(dt)

templates.env.filters.update({"money": money, "abbr": abbr, "fmtdate": fmtdate, "fmtdt": fmtdt})

# ---------- Home ----------
@router.get("/", response_class=HTMLResponse)
def page_index(
    request: Request,
    q: str | None = None,
    category: str | None = "all",
    sort: str | None = "new",
):
    all_projects = repo.list_projects()

    projects = all_projects
    if q:
        ql = q.lower()
        projects = [p for p in projects if ql in p.name.lower()]
    if category and category != "all":
        projects = [p for p in projects if p.category == category]

    today = date.today()
    items = []
    for p in projects:
        percent = min(100, int((p.raised_amount / p.goal_amount) * 100)) if p.goal_amount else 0
        days_left = (p.deadline - today).days
        items.append({
            "p": p,
            "percent": percent,
            "days_left": days_left,
            "closing_soon": 0 <= days_left <= 7,
            "fully_funded": p.raised_amount >= p.goal_amount,
        })

    if sort == "closing":
        items.sort(key=lambda x: x["p"].deadline)
    elif sort == "funded":
        items.sort(key=lambda x: x["p"].raised_amount, reverse=True)
    else:
        items.sort(key=lambda x: x["p"].project_id, reverse=True)

    categories = sorted(set(p.category for p in all_projects))
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "items": items,
            "projects": projects,
            "categories": categories,
            "q": q or "",
            "category": category or "all",
            "sort": sort or "new",
        }
    )

# ---------- Project Detail ----------
@router.get("/projects/{pid}", response_class=HTMLResponse)
def page_project_detail(pid: str, request: Request):
    p = repo.get_project(pid)
    if not p:
        raise HTTPException(404, "Project not found")
    tiers = repo.list_tiers_for_project(pid)
    percent = min(100, int((p.raised_amount / p.goal_amount) * 100)) if p.goal_amount else 0
    return templates.TemplateResponse(
        "project_detail.html",
        {"request": request, "p": p, "tiers": tiers, "percent": percent,
         "user_id": request.session.get("user_id")}
    )

@router.post("/pledge")
def do_pledge(request: Request, project_id: str = Form(...), amount: int = Form(...), tier_id: str | None = Form(None)):
    uid = request.session.get("user_id")
    if not uid:
        return RedirectResponse(url="/login", status_code=HTTP_303_SEE_OTHER)
    pledge = create_pledge(uid, project_id, amount, tier_id or None)
    request.session["flash"] = "Pledge success!" if pledge.status == "success" else f"Pledge rejected: {pledge.reject_reason}"
    return RedirectResponse(url=f"/projects/{project_id}", status_code=HTTP_303_SEE_OTHER)

# ---------- Stats (เฉพาะ user ที่ล็อกอิน) ----------
@router.get("/stats", response_class=HTMLResponse)
def page_stats(request: Request):
    uid = request.session.get("user_id")
    if not uid:
        return RedirectResponse("/login", status_code=HTTP_303_SEE_OTHER)

    succ_cnt, rej_cnt, total_amt = repo.pledge_stats_user(uid)

    my_items = []
    for pl in sorted(repo.list_pledges_by_user(uid), key=lambda x: x.created_at, reverse=True):
        proj = repo.get_project(pl.project_id)
        my_items.append({
            "pledge": pl,
            "project_name": proj.name if proj else pl.project_id,
        })

    return templates.TemplateResponse(
        "stats.html",
        {
            "request": request,
            "succ": succ_cnt,
            "rej": rej_cnt,
            "total_amt": total_amt,
            "my_items": my_items,
        }
    )

# ---------- Login / Logout ----------
@router.get("/login", response_class=HTMLResponse)
def page_login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/login")
def do_login(request: Request, username: str = Form(...), password: str = Form(...)):
    user = repo.verify_credentials(username, password)
    if not user:
        request.session["flash"] = "Invalid username or password"
        return RedirectResponse("/login", status_code=HTTP_303_SEE_OTHER)
    request.session["user_id"] = user.user_id
    request.session["display_name"] = user.display_name
    request.session["flash"] = f"Welcome, {user.display_name}!"
    return RedirectResponse("/", status_code=HTTP_303_SEE_OTHER)

@router.post("/logout")
def do_logout(request: Request):
    request.session.clear()
    return RedirectResponse("/", status_code=HTTP_303_SEE_OTHER)
