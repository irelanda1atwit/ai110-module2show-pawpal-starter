"""
pawpal_system.py — PawPal+ Logic Layer
=======================================
This module contains all backend classes for the PawPal+ pet care scheduler.
It is intentionally kept separate from the Streamlit UI (app.py) so the logic
can be tested and reasoned about independently.

Class hierarchy:
    CareTask      — a single care activity
    PetCareStats  — a pet and its list of tasks
    OwnerStats    — an owner who manages one or more pets
    PetPlanScheduler — the scheduling brain that builds a daily plan
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum


class Priority(Enum):
    """Numeric priority levels (LOW=1, MEDIUM=2, HIGH=3) used to sort tasks during scheduling."""
    LOW = 1
    MEDIUM = 2
    HIGH = 3


# ── Task ──────────────────────────────────────────────────────────────────────

@dataclass
class CareTask:
    """A single pet care activity with a title, duration, priority, and completion status."""

    title: str
    duration_minutes: int
    priority: Priority
    category: str = ""
    frequency: str = "daily"
    completed: bool = False
    scheduled_time: datetime | None = None
    pet_name: str = ""

    def mark_complete(self) -> None:
        """Mark this task as finished so the scheduler skips it in future runs."""
        self.completed = True


# ── Pet ───────────────────────────────────────────────────────────────────────

@dataclass
class PetCareStats:
    """Stores a pet's profile data and owns the list of care tasks assigned to that pet."""

    name: str
    species: str
    diet: str = ""
    medications: list[str] = field(default_factory=list)
    last_fed: datetime | None = None
    last_walked: datetime | None = None
    tasks: list[CareTask] = field(default_factory=list)

    def add_task(self, task: CareTask) -> None:
        """Attach a care task to this pet and stamp the task with this pet's name."""
        task.pet_name = self.name
        self.tasks.append(task)

    def remove_task(self, title: str) -> None:
        """Remove a task from this pet's list by its exact title."""
        self.tasks = [t for t in self.tasks if t.title != title]

    def add_medication(self, med: str) -> None:
        """Append a medication name to this pet's medication list."""
        self.medications.append(med)

    def update_last_fed(self) -> None:
        """Record the current time as this pet's most recent feeding timestamp."""
        self.last_fed = datetime.now()

    def update_last_walked(self) -> None:
        """Record the current time as this pet's most recent walk timestamp."""
        self.last_walked = datetime.now()


# ── Owner ─────────────────────────────────────────────────────────────────────

class OwnerStats:
    """Represents the pet owner, their available time, preferences, and list of pets."""

    def __init__(self, name: str, available_minutes: int, preferred_start_time: str = "08:00"):
        self.name = name
        self.available_minutes = available_minutes
        self.preferred_start_time = preferred_start_time
        self.preferences: list[str] = []
        self.pets: list[PetCareStats] = []

    def add_pet(self, pet: PetCareStats) -> None:
        """Register a pet under this owner."""
        self.pets.append(pet)

    def get_all_tasks(self) -> list[CareTask]:
        """Return a flat list of all incomplete tasks across every pet this owner manages."""
        all_tasks = []
        for pet in self.pets:
            all_tasks.extend([t for t in pet.tasks if not t.completed])
        return all_tasks

    def get_availability(self) -> int:
        """Return the number of minutes the owner has available today."""
        return self.available_minutes

    def set_preferences(self, prefs: list[str]) -> None:
        """Replace the owner's care preferences with the provided list."""
        self.preferences = prefs


# ── Scheduler ─────────────────────────────────────────────────────────────────

class PetPlanScheduler:
    """Builds a prioritized, time-stamped daily care schedule that fits within the owner's time budget."""

    def __init__(self, owner: OwnerStats):
        self.owner = owner
        self.schedule: list[CareTask] = []
        self._extra_tasks: list[CareTask] = []

    def add_task(self, task: CareTask) -> None:
        """Add a one-off task directly to the scheduler pool (not tied to a specific pet)."""
        self._extra_tasks.append(task)

    def remove_task(self, title: str) -> None:
        """Remove a task by title from all pets, the extra pool, and the active schedule."""
        for pet in self.owner.pets:
            pet.remove_task(title)
        self._extra_tasks = [t for t in self._extra_tasks if t.title != title]
        self.schedule = [t for t in self.schedule if t.title != title]

    def _total_scheduled_minutes(self) -> int:
        """Return the sum of duration_minutes for all tasks currently in the schedule."""
        return sum(t.duration_minutes for t in self.schedule)

    def _get_all_candidate_tasks(self) -> list[CareTask]:
        """Collect all incomplete tasks from the owner's pets plus any directly added tasks."""
        candidates = self.owner.get_all_tasks()
        candidates.extend([t for t in self._extra_tasks if not t.completed])
        return candidates

    def generate_schedule(self) -> list[CareTask]:
        """Sort tasks by priority (HIGH first), then greedily fit them into the owner's time budget."""
        self.schedule = []

        candidates = self._get_all_candidate_tasks()

        sorted_tasks = sorted(
            candidates,
            key=lambda t: (-t.priority.value, t.duration_minutes)
        )

        today = datetime.today()
        hour, minute = map(int, self.owner.preferred_start_time.split(":"))
        current_time = today.replace(hour=hour, minute=minute, second=0, microsecond=0)

        budget = self.owner.get_availability()

        for task in sorted_tasks:
            if task.duration_minutes <= budget:
                task.scheduled_time = current_time
                self.schedule.append(task)
                current_time += timedelta(minutes=task.duration_minutes)
                budget -= task.duration_minutes

        return self.schedule

    def explain_plan(self) -> list[str]:
        """Return a plain-English list explaining when each scheduled task runs and why it was chosen."""
        if not self.schedule:
            return ["No schedule generated yet. Call generate_schedule() first."]

        explanations = []
        for task in self.schedule:
            time_str = task.scheduled_time.strftime("%I:%M %p") if task.scheduled_time else "unscheduled"
            pet_note = f" for {task.pet_name}" if task.pet_name else ""
            explanations.append(
                f"{time_str} - {task.title}{pet_note} "
                f"({task.duration_minutes} min, {task.priority.name} priority). "
                f"Chosen because it is {task.priority.name.lower()} priority "
                f"and fits within the available time budget."
            )

        total = self._total_scheduled_minutes()
        remaining = self.owner.get_availability() - total
        explanations.append(
            f"\nTotal scheduled: {total} min | Remaining available: {remaining} min."
        )
        return explanations
