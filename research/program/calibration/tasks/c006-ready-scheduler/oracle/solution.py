"""Validate a task DAG, then greedily dispatch in stable priority order."""


def ready_tasks(tasks, capacity):
    if isinstance(capacity, bool) or not isinstance(capacity, int) or capacity < 0:
        raise ValueError("capacity must be a nonnegative integer")
    by_id = {task["id"]: task for task in tasks}
    if len(by_id) != len(tasks):
        raise ValueError("duplicate task identity")
    for task in tasks:
        if any(dep not in by_id for dep in task.get("depends_on", [])):
            raise ValueError("unknown dependency")
    visiting, complete = set(), set()

    def visit(identity):
        if identity in visiting:
            raise ValueError("dependency cycle")
        if identity in complete:
            return
        visiting.add(identity)
        for dep in by_id[identity].get("depends_on", []):
            visit(dep)
        visiting.remove(identity)
        complete.add(identity)

    for task in tasks:
        visit(task["id"])
    running = [task for task in tasks if task.get("status", "pending") == "running"]
    slots = max(0, capacity - len(running))
    occupied = {resource for task in running for resource in task.get("resources", [])}
    done = {task["id"] for task in tasks if task.get("status", "pending") == "done"}
    ordered = sorted(tasks, key=lambda task: -task.get("priority", 0))
    selected = []
    for task in ordered:
        resources = set(task.get("resources", []))
        if len(selected) >= slots:
            break
        if task.get("status", "pending") != "pending" or not all(dep in done for dep in task.get("depends_on", [])):
            continue
        if resources & occupied:
            continue
        selected.append(task["id"])
        occupied.update(resources)
    return selected
