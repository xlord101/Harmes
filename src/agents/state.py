from typing import TypedDict, List, Optional
from pydantic import BaseModel, Field

class Issue(BaseModel):
    id: str
    title: str
    url: str
    description: str
    repository: str = ""
    labels: List[str] = Field(default_factory=list)
    tech_stack: List[str] = Field(default_factory=list)
    score: int = 0
    is_published: bool = False

class AgentState(TypedDict, total=False):
    target_repos: List[str]
    limit: int
    difficulty_levels: List[str]
    global_search_first: bool
    raw_issues: List[dict]
    evaluated_issues: List[Issue]
    post_draft: str

