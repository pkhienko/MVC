from datetime import datetime
from app.models.entities import Pledge, check_pledge_rules
from app.models import repo_csv as repo

def create_pledge(user_id: str, project_id: str, amount: int, tier_id: str | None) -> Pledge:
    project = repo.get_project(project_id)
    if not project:
        return Pledge("NA", user_id, project_id, datetime.now(), amount, tier_id, "rejected", "Project not found")

    tier = None
    reason = None
    if tier_id:
        tier = repo.get_tier(project_id, tier_id)
        if not tier:
            reason = "Tier not found"

    if reason is None:
        reason = check_pledge_rules(amount, project, tier)

    status = "success" if reason is None else "rejected"

    pledge = Pledge(
        pledge_id=f"PL{int(datetime.now().timestamp()*1000)}",
        user_id=user_id,
        project_id=project_id,
        created_at=datetime.now(),
        amount=amount,
        tier_id=tier_id,
        status=status,
        reject_reason=reason
    )
    repo.add_pledge(pledge)

    if status == "success":
        project.raised_amount += amount
        repo.update_project(project)
        if tier:
            tier.quota = max(0, tier.quota - 1)
            repo.update_tier(tier)

    return pledge