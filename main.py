"""
main.py -PawPal+ live demo
===========================
Demonstrates scheduling, sort_by_time(), and filter_tasks().

    python main.py
"""

from pawpal_system import CareTask, PetCareStats, OwnerStats, PetPlanScheduler, Priority


def separator(label: str) -> None:
    print(f"\n{'-' * 50}")
    print(f"  {label}")
    print(f"{'-' * 50}")


def main() -> None:
    # ── 1. Owner ──────────────────────────────────────────────────────────────
    separator("1. Owner setup")
    owner = OwnerStats(name="Jordan", available_minutes=90, preferred_start_time="08:00")
    owner.set_preferences(["no early walks", "keep sessions under 30 min"])
    print(f"Owner: {owner.name}  |  Available: {owner.get_availability()} min  |  Start: {owner.preferred_start_time}")

    # ── 2. Pets ───────────────────────────────────────────────────────────────
    separator("2. Pet setup")
    mochi    = PetCareStats(name="Mochi",    species="dog", diet="grain-free kibble")
    whiskers = PetCareStats(name="Whiskers", species="cat")
    mochi.add_medication("Apoquel 16mg")
    owner.add_pet(mochi)
    owner.add_pet(whiskers)
    print(f"Pets: {[p.name for p in owner.pets]}  |  Mochi meds: {mochi.medications}")

    # ── 3. Tasks added intentionally OUT OF ORDER ─────────────────────────────
    #   (LOW tasks first, then HIGH -scheduler must re-sort by priority)
    separator("3. Tasks added out of order (LOW -> MEDIUM -> HIGH)")
    whiskers.add_task(CareTask("Laser toy play", 15, Priority.LOW,    "exercise"))   # LOW
    mochi.add_task(   CareTask("Backyard playtime", 20, Priority.LOW,  "exercise"))  # LOW
    whiskers.add_task(CareTask("Clean litter",   10, Priority.MEDIUM, "hygiene"))    # MEDIUM
    mochi.add_task(   CareTask("Brush coat",     15, Priority.MEDIUM, "grooming"))   # MEDIUM
    whiskers.add_task(CareTask("Feed Whiskers",   5, Priority.HIGH,   "feeding"))    # HIGH
    mochi.add_task(   CareTask("Give Apoquel",    2, Priority.HIGH,   "medication")) # HIGH
    mochi.add_task(   CareTask("Feed Mochi",      5, Priority.HIGH,   "feeding"))    # HIGH
    mochi.add_task(   CareTask("Morning walk",   30, Priority.HIGH,   "exercise"))   # HIGH

    print("Insertion order:")
    for pet in owner.pets:
        for t in pet.tasks:
            print(f"  [{t.priority.name:<6}] {t.title} ({t.duration_minutes} min) - {pet.name}")

    # ── 4. Generate schedule (sorts HIGH → LOW internally) ────────────────────
    separator("4. Generate schedule")
    scheduler = PetPlanScheduler(owner=owner)
    schedule  = scheduler.generate_schedule()
    print(f"Scheduled {len(schedule)} / {len(owner.get_all_tasks())} tasks")

    # ── 5. sort_by_time() ─────────────────────────────────────────────────────
    separator("5. sort_by_time() -chronological view")
    for t in scheduler.sort_by_time():
        time_str = t.scheduled_time.strftime("%H:%M") if t.scheduled_time else "??:??"
        print(f"  {time_str}  [{t.priority.name:<6}]  {t.title} -{t.pet_name}")

    # ── 6. filter_tasks() by pet name ─────────────────────────────────────────
    separator("6. filter_tasks(pet_name='Mochi')")
    for t in scheduler.filter_tasks(pet_name="Mochi"):
        time_str = t.scheduled_time.strftime("%H:%M") if t.scheduled_time else "??:??"
        print(f"  {time_str}  {t.title}  ({t.priority.name})")

    separator("6b. filter_tasks(pet_name='Whiskers')")
    for t in scheduler.filter_tasks(pet_name="Whiskers"):
        time_str = t.scheduled_time.strftime("%H:%M") if t.scheduled_time else "??:??"
        print(f"  {time_str}  {t.title}  ({t.priority.name})")

    # ── 7. filter_tasks() by completion status ────────────────────────────────
    separator("7. Mark 'Morning walk' complete -filter by completed status")
    mochi.tasks[-1].mark_complete()          # Morning walk was added last
    scheduler.generate_schedule()            # refresh -completed task drops out

    print("  Incomplete tasks:")
    for t in scheduler.filter_tasks(completed=False):
        print(f"    {t.title} -{t.pet_name}")

    print("\n  Completed tasks (not in schedule, shown from pet list):")
    done = [t for pet in owner.pets for t in pet.tasks if t.completed]
    for t in done:
        print(f"    {t.title} -{t.pet_name}")

    # ── 8. Combined filter: Mochi + incomplete ────────────────────────────────
    separator("8. filter_tasks(pet_name='Mochi', completed=False)")
    for t in scheduler.filter_tasks(pet_name="Mochi", completed=False):
        time_str = t.scheduled_time.strftime("%H:%M") if t.scheduled_time else "??:??"
        print(f"  {time_str}  {t.title}")

    # ── 9. Auto-recurrence via mark_task_complete() ───────────────────────────
    separator("9. Auto-recurrence: mark_task_complete('Feed Mochi')")
    recurrence = scheduler.mark_task_complete("Feed Mochi")

    if recurrence:
        print(f"  Original 'Feed Mochi'  -> completed")
        print(f"  New recurrence created -> '{recurrence.title}'")
        print(f"  Frequency              : {recurrence.frequency}")
        print(f"  Next due date          : {recurrence.due_date.strftime('%Y-%m-%d')} "
              f"(today + 1 day via timedelta(days=1))")

    separator("9b. Auto-recurrence: mark_task_complete('Clean litter') [weekly]")
    # Change frequency on whiskers' litter task to weekly for demo
    for t in whiskers.tasks:
        if t.title == "Clean litter":
            t.frequency = "weekly"
    recurrence2 = scheduler.mark_task_complete("Clean litter")

    if recurrence2:
        print(f"  Original 'Clean litter' -> completed")
        print(f"  New recurrence created  -> '{recurrence2.title}'")
        print(f"  Frequency               : {recurrence2.frequency}")
        print(f"  Next due date           : {recurrence2.due_date.strftime('%Y-%m-%d')} "
              f"(today + 7 days via timedelta(days=7))")

    separator("9c. Schedule after recurrence (new tasks appear as incomplete)")
    scheduler.generate_schedule()
    for t in scheduler.sort_by_time():
        due = f"  due {t.due_date.strftime('%Y-%m-%d')}" if t.due_date else ""
        time_str = t.scheduled_time.strftime("%H:%M") if t.scheduled_time else "??:??"
        print(f"  {time_str}  [{t.priority.name:<6}]  {t.title} ({t.pet_name}){due}")

    # ── 10. Conflict detection ────────────────────────────────────────────────
    # Force two tasks onto the identical scheduled_time to trigger a conflict.
    separator("10. Conflict detection demo")

    from datetime import datetime as dt
    clash_time = dt.today().replace(hour=9, minute=0, second=0, microsecond=0)

    # Grab the first two scheduled tasks and pin them to 09:00
    if len(scheduler.schedule) >= 2:
        scheduler.schedule[0].scheduled_time = clash_time
        scheduler.schedule[1].scheduled_time = clash_time
        print(f"  Manually set '{scheduler.schedule[0].title}' and "
              f"'{scheduler.schedule[1].title}' to 09:00 to simulate a conflict.\n")

    conflicts = scheduler.detect_conflicts()
    if conflicts:
        for warning in conflicts:
            print(f"  {warning}")
    else:
        print("  No conflicts detected.")

    # Show that a clean schedule produces no warnings
    separator("10b. No-conflict check (fresh schedule)")
    mochi2  = PetCareStats(name="Buddy", species="dog")
    owner2  = OwnerStats(name="Alex", available_minutes=60, preferred_start_time="07:00")
    owner2.add_pet(mochi2)
    mochi2.add_task(CareTask("Morning run", 20, Priority.HIGH,   "exercise"))
    mochi2.add_task(CareTask("Feed Buddy",   5, Priority.HIGH,   "feeding"))
    mochi2.add_task(CareTask("Grooming",    15, Priority.MEDIUM, "grooming"))

    clean_scheduler = PetPlanScheduler(owner=owner2)
    clean_scheduler.generate_schedule()

    for t in clean_scheduler.sort_by_time():
        time_str = t.scheduled_time.strftime("%H:%M") if t.scheduled_time else "??:??"
        print(f"  {time_str}  {t.title}")

    clean_conflicts = clean_scheduler.detect_conflicts()
    print(f"\n  Conflicts detected: {len(clean_conflicts)} (expected 0)")


if __name__ == "__main__":
    main()
