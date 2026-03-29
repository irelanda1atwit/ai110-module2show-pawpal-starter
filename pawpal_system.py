from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class CareTask:
    title: str
    duration_minutes: int
    priority: str  # "low", "medium", "high"
    category: str = ""
    completed: bool = False

    def mark_complete(self) -> None:
        pass


@dataclass
class PetCareStats:
    name: str
    species: str
    diet: str = ""
    medications: list[str] = field(default_factory=list)
    last_fed: datetime | None = None
    last_walked: datetime | None = None

    def add_medication(self, med: str) -> None:
        pass

    def update_last_fed(self) -> None:
        pass

    def update_last_walked(self) -> None:
        pass


class OwnerStats:
    def __init__(self, name: str, available_minutes: int, preferred_start_time: str = "08:00"):
        self.name = name
        self.available_minutes = available_minutes
        self.preferred_start_time = preferred_start_time
        self.preferences: list[str] = []

    def get_availability(self) -> int:
        pass

    def set_preferences(self, prefs: list[str]) -> None:
        pass


class PetPlanScheduler:
    def __init__(self, owner: OwnerStats, pet: PetCareStats):
        self.owner = owner
        self.pet = pet
        self.tasks: list[CareTask] = []
        self.schedule: list[CareTask] = []

    def add_task(self, task: CareTask) -> None:
        pass

    def remove_task(self, title: str) -> None:
        pass

    def generate_schedule(self) -> list[CareTask]:
        pass

    def explain_plan(self) -> str:
        pass
