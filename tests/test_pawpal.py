"""
tests/test_pawpal.py — Pytest suite for PawPal+ logic layer
============================================================
Run with:
    pytest tests/test_pawpal.py -v
"""

import pytest
from datetime import datetime
from pawpal_system import CareTask, PetCareStats, OwnerStats, PetPlanScheduler, Priority


# ── Fixtures ──────────────────────────────────────────────────────────────────
# Reusable objects shared across tests.

@pytest.fixture
def basic_task():
    """A simple HIGH-priority 20-minute task."""
    return CareTask(title="Morning walk", duration_minutes=20, priority=Priority.HIGH, category="exercise")


@pytest.fixture
def short_task():
    """A LOW-priority 5-minute task."""
    return CareTask(title="Feed pet", duration_minutes=5, priority=Priority.LOW, category="feeding")


@pytest.fixture
def dog():
    """A dog pet with no tasks."""
    return PetCareStats(name="Mochi", species="dog", diet="grain-free")


@pytest.fixture
def cat():
    """A cat pet with no tasks."""
    return PetCareStats(name="Whiskers", species="cat")


@pytest.fixture
def owner(dog, cat):
    """An owner with 90 minutes available, managing two pets."""
    o = OwnerStats(name="Jordan", available_minutes=90, preferred_start_time="08:00")
    o.add_pet(dog)
    o.add_pet(cat)
    return o


@pytest.fixture
def scheduler(owner):
    """A scheduler built from the standard owner fixture."""
    return PetPlanScheduler(owner=owner)


# ── CareTask Tests ────────────────────────────────────────────────────────────

class TestCareTask:

    def test_task_completion_changes_status(self, basic_task):
        """mark_complete() must flip completed from False to True."""
        assert basic_task.completed is False
        basic_task.mark_complete()
        assert basic_task.completed is True

    def test_mark_complete_is_idempotent(self, basic_task):
        """Calling mark_complete() twice should not raise and stays True."""
        basic_task.mark_complete()
        basic_task.mark_complete()
        assert basic_task.completed is True

    def test_task_default_values(self, basic_task):
        """Newly created tasks should have sensible defaults."""
        assert basic_task.scheduled_time is None
        assert basic_task.pet_name == ""
        assert basic_task.frequency == "daily"
        assert basic_task.completed is False

    def test_priority_ordering(self):
        """HIGH priority must have a greater value than MEDIUM and LOW."""
        assert Priority.HIGH.value > Priority.MEDIUM.value > Priority.LOW.value

    def test_task_stores_duration(self):
        """Task duration should be stored exactly as provided."""
        task = CareTask(title="Groom", duration_minutes=45, priority=Priority.MEDIUM)
        assert task.duration_minutes == 45


# ── PetCareStats Tests ────────────────────────────────────────────────────────

class TestPetCareStats:

    def test_add_task_increases_count(self, dog, basic_task):
        """Adding a task to a pet must increase its task list length by 1."""
        before = len(dog.tasks)
        dog.add_task(basic_task)
        assert len(dog.tasks) == before + 1

    def test_add_multiple_tasks_increases_count(self, dog, basic_task, short_task):
        """Adding two tasks should increase the task count by 2."""
        dog.add_task(basic_task)
        dog.add_task(short_task)
        assert len(dog.tasks) == 2

    def test_add_task_stamps_pet_name(self, dog, basic_task):
        """add_task() must set task.pet_name to the pet's name."""
        dog.add_task(basic_task)
        assert basic_task.pet_name == "Mochi"

    def test_remove_task_decreases_count(self, dog, basic_task):
        """remove_task() must reduce the task list by 1."""
        dog.add_task(basic_task)
        assert len(dog.tasks) == 1
        dog.remove_task("Morning walk")
        assert len(dog.tasks) == 0

    def test_remove_nonexistent_task_does_nothing(self, dog):
        """Removing a task that doesn't exist should not raise or change state."""
        dog.remove_task("Ghost task")
        assert len(dog.tasks) == 0

    def test_add_medication(self, dog):
        """add_medication() must append the med to the medications list."""
        dog.add_medication("Apoquel 16mg")
        assert "Apoquel 16mg" in dog.medications

    def test_add_multiple_medications(self, dog):
        """Multiple medications should all appear in the list."""
        dog.add_medication("Apoquel 16mg")
        dog.add_medication("Probiotic")
        assert len(dog.medications) == 2

    def test_update_last_fed(self, dog):
        """update_last_fed() must set last_fed to a recent datetime."""
        assert dog.last_fed is None
        before = datetime.now()
        dog.update_last_fed()
        assert dog.last_fed is not None
        assert dog.last_fed >= before

    def test_update_last_walked(self, dog):
        """update_last_walked() must set last_walked to a recent datetime."""
        assert dog.last_walked is None
        before = datetime.now()
        dog.update_last_walked()
        assert dog.last_walked is not None
        assert dog.last_walked >= before


# ── OwnerStats Tests ──────────────────────────────────────────────────────────

class TestOwnerStats:

    def test_add_pet_increases_count(self, dog):
        """Adding a pet to an owner must increase pets list by 1."""
        o = OwnerStats(name="Sam", available_minutes=60)
        assert len(o.pets) == 0
        o.add_pet(dog)
        assert len(o.pets) == 1

    def test_get_availability_returns_minutes(self):
        """get_availability() must return the exact available_minutes value."""
        o = OwnerStats(name="Sam", available_minutes=45)
        assert o.get_availability() == 45

    def test_set_preferences(self):
        """set_preferences() must replace the preferences list."""
        o = OwnerStats(name="Sam", available_minutes=60)
        o.set_preferences(["no early walks", "short sessions"])
        assert o.preferences == ["no early walks", "short sessions"]

    def test_set_preferences_replaces_existing(self):
        """Calling set_preferences() twice must use the latest list."""
        o = OwnerStats(name="Sam", available_minutes=60)
        o.set_preferences(["first pref"])
        o.set_preferences(["updated pref"])
        assert o.preferences == ["updated pref"]

    def test_get_all_tasks_collects_across_pets(self, owner, dog, cat, basic_task, short_task):
        """get_all_tasks() must return tasks from all pets in one flat list."""
        dog.add_task(basic_task)
        cat.add_task(short_task)
        all_tasks = owner.get_all_tasks()
        assert len(all_tasks) == 2

    def test_get_all_tasks_excludes_completed(self, owner, dog, basic_task):
        """Completed tasks must not appear in get_all_tasks()."""
        dog.add_task(basic_task)
        basic_task.mark_complete()
        all_tasks = owner.get_all_tasks()
        assert len(all_tasks) == 0

    def test_get_all_tasks_empty_with_no_pets(self):
        """An owner with no pets should return an empty task list."""
        o = OwnerStats(name="Empty", available_minutes=60)
        assert o.get_all_tasks() == []


# ── PetPlanScheduler Tests ────────────────────────────────────────────────────

class TestPetPlanScheduler:

    def test_generate_schedule_respects_budget(self, owner, dog):
        """Scheduler must not exceed the owner's available_minutes."""
        dog.add_task(CareTask(title="Task A", duration_minutes=50, priority=Priority.HIGH))
        dog.add_task(CareTask(title="Task B", duration_minutes=50, priority=Priority.HIGH))
        scheduler = PetPlanScheduler(owner=owner)
        scheduler.generate_schedule()
        assert scheduler._total_scheduled_minutes() <= owner.available_minutes

    def test_generate_schedule_high_priority_first(self, owner, dog):
        """HIGH-priority tasks must appear before LOW-priority tasks in the schedule."""
        dog.add_task(CareTask(title="Low task",  duration_minutes=10, priority=Priority.LOW))
        dog.add_task(CareTask(title="High task", duration_minutes=10, priority=Priority.HIGH))
        scheduler = PetPlanScheduler(owner=owner)
        schedule = scheduler.generate_schedule()
        titles = [t.title for t in schedule]
        assert titles.index("High task") < titles.index("Low task")

    def test_generate_schedule_assigns_scheduled_time(self, owner, dog, basic_task):
        """Every scheduled task must have a scheduled_time set."""
        dog.add_task(basic_task)
        scheduler = PetPlanScheduler(owner=owner)
        schedule = scheduler.generate_schedule()
        for task in schedule:
            assert task.scheduled_time is not None

    def test_generate_schedule_excludes_completed_tasks(self, owner, dog, basic_task):
        """Completed tasks must not appear in the generated schedule."""
        basic_task.mark_complete()
        dog.add_task(basic_task)
        scheduler = PetPlanScheduler(owner=owner)
        schedule = scheduler.generate_schedule()
        assert basic_task not in schedule

    def test_generate_schedule_zero_budget(self, dog):
        """An owner with 0 minutes available should produce an empty schedule."""
        broke_owner = OwnerStats(name="Tired", available_minutes=0)
        broke_owner.add_pet(dog)
        dog.add_task(CareTask(title="Walk", duration_minutes=20, priority=Priority.HIGH))
        scheduler = PetPlanScheduler(owner=broke_owner)
        schedule = scheduler.generate_schedule()
        assert schedule == []

    def test_generate_schedule_no_tasks(self, owner):
        """A scheduler with no tasks should return an empty schedule."""
        scheduler = PetPlanScheduler(owner=owner)
        schedule = scheduler.generate_schedule()
        assert schedule == []

    def test_total_scheduled_minutes_is_accurate(self, owner, dog):
        """_total_scheduled_minutes() must match the sum of scheduled task durations."""
        dog.add_task(CareTask(title="Task A", duration_minutes=15, priority=Priority.HIGH))
        dog.add_task(CareTask(title="Task B", duration_minutes=20, priority=Priority.MEDIUM))
        scheduler = PetPlanScheduler(owner=owner)
        scheduler.generate_schedule()
        assert scheduler._total_scheduled_minutes() == 35

    def test_remove_task_from_scheduler(self, owner, dog):
        """remove_task() must remove the task from the pet's list."""
        task = CareTask(title="Groom", duration_minutes=15, priority=Priority.LOW)
        dog.add_task(task)
        scheduler = PetPlanScheduler(owner=owner)
        scheduler.remove_task("Groom")
        assert all(t.title != "Groom" for t in dog.tasks)

    def test_explain_plan_before_schedule(self, scheduler):
        """explain_plan() before generate_schedule() must return a helpful message."""
        result = scheduler.explain_plan()
        assert len(result) == 1
        assert "generate_schedule" in result[0]

    def test_explain_plan_returns_one_entry_per_task(self, owner, dog):
        """explain_plan() must return one line per scheduled task plus a summary."""
        dog.add_task(CareTask(title="Walk",  duration_minutes=10, priority=Priority.HIGH))
        dog.add_task(CareTask(title="Feed",  duration_minutes=5,  priority=Priority.HIGH))
        scheduler = PetPlanScheduler(owner=owner)
        scheduler.generate_schedule()
        explanations = scheduler.explain_plan()
        # 2 tasks + 1 summary line
        assert len(explanations) == 3

    def test_schedule_rebuilds_after_completion(self, owner, dog):
        """After marking a task complete, re-running generate_schedule() excludes it."""
        task = CareTask(title="Walk", duration_minutes=20, priority=Priority.HIGH)
        dog.add_task(task)
        scheduler = PetPlanScheduler(owner=owner)
        scheduler.generate_schedule()
        assert task in scheduler.schedule

        task.mark_complete()
        scheduler.generate_schedule()
        assert task not in scheduler.schedule

    def test_shorter_tasks_used_as_tiebreak(self, owner, dog):
        """When two tasks share the same priority, shorter one should be scheduled first."""
        dog.add_task(CareTask(title="Long",  duration_minutes=30, priority=Priority.MEDIUM))
        dog.add_task(CareTask(title="Short", duration_minutes=5,  priority=Priority.MEDIUM))
        scheduler = PetPlanScheduler(owner=owner)
        schedule = scheduler.generate_schedule()
        titles = [t.title for t in schedule]
        assert titles.index("Short") < titles.index("Long")
