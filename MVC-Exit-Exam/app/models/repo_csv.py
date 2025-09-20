import csv, threading
from pathlib import Path
from datetime import datetime, date
from typing import List, Optional, Tuple
from .entities import Project, RewardTier, User, Pledge

BASE = Path(__file__).resolve().parent / "data"
_lock = threading.Lock()

def _read_csv(name: str) -> list[dict]:
    path = BASE / name
    with _lock, path.open("r", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def _write_csv(name: str, rows: list[dict], fieldnames: list[str]):
    path = BASE / name
    with _lock, path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow(r)

# ---------- Projects ----------
def list_projects() -> List[Project]:
    rows = _read_csv("projects.csv")
    return [Project(
        project_id=r["project_id"],
        name=r["name"],
        category=r["category"],
        goal_amount=int(r["goal_amount"]),
        deadline=date.fromisoformat(r["deadline"]),
        raised_amount=int(r["raised_amount"])
    ) for r in rows]

def get_project(pid: str) -> Optional[Project]:
    return next((p for p in list_projects() if p.project_id == pid), None)

def update_project(p: Project):
    rows = _read_csv("projects.csv")
    for i, r in enumerate(rows):
        if r["project_id"] == p.project_id:
            rows[i] = {
                "project_id": p.project_id,
                "name": p.name,
                "category": p.category,
                "goal_amount": str(p.goal_amount),
                "deadline": p.deadline.isoformat(),
                "raised_amount": str(p.raised_amount)
            }
            _write_csv("projects.csv", rows, ["project_id","name","category","goal_amount","deadline","raised_amount"])
            return

# ---------- Reward Tiers ----------
def list_tiers_for_project(pid: str) -> List[RewardTier]:
    rows = _read_csv("reward_tiers.csv")
    return [RewardTier(
        project_id=r["project_id"],
        tier_id=r["tier_id"],
        name=r["name"],
        min_amount=int(r["min_amount"]),
        quota=int(r["quota"])
    ) for r in rows if r["project_id"] == pid]

def get_tier(pid: str, tid: str) -> Optional[RewardTier]:
    return next((t for t in list_tiers_for_project(pid) if t.tier_id == tid), None)

def update_tier(t: RewardTier):
    rows = _read_csv("reward_tiers.csv")
    for i, r in enumerate(rows):
        if r["project_id"] == t.project_id and r["tier_id"] == t.tier_id:
            rows[i] = {
                "project_id": t.project_id,
                "tier_id": t.tier_id,
                "name": t.name,
                "min_amount": str(t.min_amount),
                "quota": str(t.quota)
            }
            _write_csv("reward_tiers.csv", rows, ["project_id","tier_id","name","min_amount","quota"])
            return

# ---------- Users ----------
def list_users() -> List[User]:
    rows = _read_csv("users.csv")
    return [User(
        user_id=r["user_id"],
        username=r["username"],
        password=r["password"],
        display_name=r["display_name"]
    ) for r in rows]

def get_user(uid: str) -> Optional[User]:
    return next((u for u in list_users() if u.user_id == uid), None)

def get_user_by_username(username: str) -> Optional[User]:
    return next((u for u in list_users() if u.username == username), None)

def verify_credentials(username: str, password: str) -> Optional[User]:
    u = get_user_by_username(username)
    if u and u.password == password:
        return u
    return None

# ---------- Pledges & Stats ----------
def list_pledges() -> List[Pledge]:
    rows = _read_csv("pledges.csv")
    return [Pledge(
        pledge_id=r["pledge_id"],
        user_id=r["user_id"],
        project_id=r["project_id"],
        created_at=datetime.fromisoformat(r["created_at"]),
        amount=int(r["amount"]),
        tier_id=r["tier_id"] or None,
        status=r["status"],
        reject_reason=r["reject_reason"] or None
    ) for r in rows]

def add_pledge(pl: Pledge):
    rows = _read_csv("pledges.csv")
    rows.append({
        "pledge_id": pl.pledge_id,
        "user_id": pl.user_id,
        "project_id": pl.project_id,
        "created_at": pl.created_at.isoformat(),
        "amount": str(pl.amount),
        "tier_id": pl.tier_id or "",
        "status": pl.status,
        "reject_reason": pl.reject_reason or ""
    })
    _write_csv("pledges.csv", rows, ["pledge_id","user_id","project_id","created_at","amount","tier_id","status","reject_reason"])

def pledge_stats() -> Tuple[int, int]:
    items = list_pledges()
    succ = sum(1 for p in items if p.status == "success")
    rej  = sum(1 for p in items if p.status == "rejected")
    return succ, rej

def list_pledges_by_user(user_id: str) -> List[Pledge]:
    return [p for p in list_pledges() if p.user_id == user_id]

def pledge_stats_user(user_id: str) -> tuple[int, int, int]:
    items = list_pledges_by_user(user_id)
    succ = [p for p in items if p.status == "success"]
    rej  = [p for p in items if p.status == "rejected"]
    total_amt = sum(p.amount for p in succ)
    return len(succ), len(rej), total_amt
