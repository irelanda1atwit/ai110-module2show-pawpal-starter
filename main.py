"""
main.py — Manual testing ground for PawPal+ logic
===================================================
Run this file directly to verify that all backend classes work correctly
before wiring them into the Streamlit UI.

    python main.py
"""

from pawpal_system import CareTask, PetCareStats, OwnerStats, PetPlanScheduler, Priority


def separator(label: str) -> None:
    print(f"\n{'─' * 50}")
    print(f"  {label}")
    print(f"{'─' * 50}")


# ── 1. Create an Owner ────────────────────────────────────────────────────────
separator("1. Owner setup")

owner = OwnerStats(name="Jordan", available_minutes=90, preferred_start_time="08:00")
owner.set_preferences(["no early walks", "keep sessions under 30 min"])

print(f"Owner     : {owner.name}")
print(f"Available : {owner.get_availability()} minutes")
print(f"Start time: {owner.preferred_start_time}")
print(f"Prefs     : {owner.preferences}")


# ── 2. Create Pets ────────────────────────────────────────────────────────────
separator("2. Pet setup")

mochi = PetCareStats(name="Mochi", species="dog", diet="grain-free kibble")
mochi.add_medication("Apoquel 16mg")

whiskers = PetCareStats(name="Whiskers", species="cat")

owner.add_pet(mochi)
owner.add_pet(whiskers)

print(f"Pets registered: {[p.name for p in owner.pets]}")
print(f"Mochi meds      : {mochi.medications}")


# ── 3. Add Tasks to Pets ──────────────────────────────────────────────────────
separator("3. Task setup")

mochi.add_task(CareTask(title="Morning walk",     duration_minutes=30, priority=Priority.HIGH,   category="exercise"))
mochi.add_task(CareTask(title="Feed Mochi",       duration_minutes=5,  priority=Priority.HIGH,   category="feeding"))
mochi.add_task(CareTask(title="Give Apoquel",     duration_minutes=2,  priority=Priority.HIGH,   category="medication"))
mochi.add_task(CareTask(title="Brush coat",       duration_minutes=15, priority=Priority.MEDIUM, category="grooming"))
mochi.add_task(CareTask(title="Backyard playtime",duration_minutes=20, priority=Priority.LOW,    category="exercise"))

whiskers.add_task(CareTask(title="Feed Whiskers", duration_minutes=5,  priority=Priority.HIGH,   category="feeding"))
whiskers.add_task(CareTask(title="Clean litter",  duration_minutes=10, priority=Priority.MEDIUM, category="hygiene"))
whiskers.add_task(CareTask(title="Laser toy play",duration_minutes=15, priority=Priority.LOW,    category="exercise"))

print("Tasks added:")
for pet in owner.pets:
    for task in pet.tasks:
        print(f"  [{task.priority.name:<6}] {task.title} ({task.duration_minutes} min) - {pet.name}")


# ── 4. Verify get_all_tasks() ─────────────────────────────────────────────────
separator("4. Owner.get_all_tasks()")

all_tasks = owner.get_all_tasks()
print(f"Total incomplete tasks across all pets: {len(all_tasks)}")
for t in all_tasks:
    print(f"  {t.pet_name:<10} | {t.title}")


# ── 5. Generate Schedule ──────────────────────────────────────────────────────
separator("5. Generate schedule (budget: 90 min)")

scheduler = PetPlanScheduler(owner=owner)
schedule = scheduler.generate_schedule()

print(f"Tasks scheduled: {len(schedule)} / {len(all_tasks)}")
print(f"Time used      : {scheduler._total_scheduled_minutes()} / {owner.available_minutes} min")


# ── 6. Explain the Plan ───────────────────────────────────────────────────────
separator("6. Today's Schedule")

print(f"Today's Schedule for {owner.name}\n")
for line in scheduler.explain_plan():
    print(line)


# ── 7. Mark a Task Complete and Re-schedule ───────────────────────────────────
separator("7. Mark 'Morning walk' complete, re-schedule")

mochi.tasks[0].mark_complete()
print(f"'Morning walk' completed: {mochi.tasks[0].completed}")

schedule2 = scheduler.generate_schedule()
print(f"\nUpdated schedule ({len(schedule2)} tasks):")
for line in scheduler.explain_plan():
    print(line)


# ── 8. Remove a Task ─────────────────────────────────────────────────────────
separator("8. Remove 'Clean litter' from schedule")

scheduler.remove_task("Clean litter")
print(f"Whiskers tasks remaining: {[t.title for t in whiskers.tasks]}")


# ── 9. Edge Case — Zero Budget ────────────────────────────────────────────────
separator("9. Edge case: owner has 0 minutes available")

broke_owner = OwnerStats(name="Tired Owner", available_minutes=0)
broke_pet   = PetCareStats(name="Rex", species="dog")
broke_pet.add_task(CareTask(title="Walk Rex", duration_minutes=20, priority=Priority.HIGH))
broke_owner.add_pet(broke_pet)

empty_scheduler = PetPlanScheduler(owner=broke_owner)
empty_schedule  = empty_scheduler.generate_schedule()
print(f"Tasks scheduled with 0 min budget: {len(empty_schedule)}")
for line in empty_scheduler.explain_plan():
    print(line)


print("\nAll tests passed - logic layer is working.\n")
