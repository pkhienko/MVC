from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional

@dataclass
class Project:
    project_id: str
    name: str
    category: str
    goal_amount: int
    deadline: date
    raised_amount: int

    def validate(self, today: Optional[date] = None):
        t = today or date.today()
        if not (len(self.project_id) == 8 and self.project_id.isdigit() and self.project_id[0] != "0"):
            raise ValueError("Project ID must be 8 digits and not start with 0")
        if self.goal_amount <= 0:
            raise ValueError("Goal must be > 0")
        if self.deadline <= t:
            raise ValueError("Deadline must be in the future")

@dataclass
class RewardTier:
    project_id: str
    tier_id: str
    name: str
    min_amount: int
    quota: int

    def validate(self):
        if self.min_amount < 0:
            raise ValueError("Min amount must be >= 0")
        if self.quota < 0:
            raise ValueError("Quota must be >= 0")

@dataclass
class User:
    user_id: str
    username: str
    password: str
    display_name: str

@dataclass
class Pledge:
    pledge_id: str
    user_id: str
    project_id: str
    created_at: datetime
    amount: int
    tier_id: Optional[str]
    status: str
    reject_reason: Optional[str] = None

def check_pledge_rules(amount: int, project: Project, tier: Optional[RewardTier], now: Optional[datetime] = None) -> Optional[str]:
    dt = now or datetime.now()
    if project.deadline <= dt.date():
        return "Project deadline passed"
    if amount <= 0:
        return "Amount must be > 0"
    if tier:
        if amount < tier.min_amount:
            return "Amount below tier minimum"
        if tier.quota <= 0:
            return "Tier sold out"
    return None
