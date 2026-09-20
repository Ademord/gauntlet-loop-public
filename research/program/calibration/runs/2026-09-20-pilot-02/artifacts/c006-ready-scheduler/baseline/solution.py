"""Choose pending tasks that can be dispatched next."""


def ready_tasks(tasks, capacity):
    if isinstance(capacity, bool) or not isinstance(capacity, int) or capacity < 0:
        raise ValueError("capacity must be a non-negative integer")

    seen_ids = set()
    for task in tasks:
        task_id = task["id"]
        if task_id in seen_ids:
            raise ValueError(f"duplicate task id: {task_id}")
        seen_ids.add(task_id)

    for task in tasks:
        for dep in task.get("depends_on", []):
            if dep not in seen_ids:
                raise ValueError(f"unknown dependency: {dep}")

    depends_on_map = {task["id"]: task.get("depends_on", []) for task in tasks}
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {task_id: WHITE for task_id in seen_ids}

    def visit(task_id):
        color[task_id] = GRAY
        for dep in depends_on_map[task_id]:
            if color[dep] == GRAY:
                raise ValueError(f"dependency cycle detected involving: {dep}")
            if color[dep] == WHITE:
                visit(dep)
        color[task_id] = BLACK

    for task_id in seen_ids:
        if color[task_id] == WHITE:
            visit(task_id)

    running_count = sum(1 for task in tasks if task.get("status", "pending") == "running")
    reserved_resources = set()
    for task in tasks:
        if task.get("status", "pending") == "running":
            reserved_resources.update(task.get("resources", []))

    slots = max(0, capacity - running_count)
    if slots == 0:
        return []

    done_ids = {task["id"] for task in tasks if task.get("status", "pending") == "done"}
    eligible = [
        task
        for task in tasks
        if task.get("status", "pending") == "pending"
        and all(dep in done_ids for dep in task.get("depends_on", []))
    ]
    eligible.sort(key=lambda task: -task.get("priority", 0))

    selected = []
    for task in eligible:
        if len(selected) >= slots:
            break
        resources = set(task.get("resources", []))
        if resources & reserved_resources:
            continue
        selected.append(task["id"])
        reserved_resources.update(resources)

    return selected
