from pydantic import BaseModel, Field

class ProjectOut(BaseModel):
    project_id: str
    name: str
    category: str
    goal_amount: int
    deadline: str
    raised_amount: int

class PledgeIn(BaseModel):
    project_id: str = Field(..., min_length=8, max_length=8)
    amount: int = Field(..., gt=0)
    tier_id: str | None = None