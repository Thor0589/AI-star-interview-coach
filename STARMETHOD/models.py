from dataclasses import dataclass, asdict
from typing import Optional

@dataclass
class Story:
    competency: str
    question: str
    situation: str
    task: str
    action: str
    result: str
    score: Optional[str] = None
    timestamp: Optional[str] = None # Added for sorting/tracking

    def to_dict(self):
        """Convert dataclass instance to dictionary."""
        return asdict(self)
