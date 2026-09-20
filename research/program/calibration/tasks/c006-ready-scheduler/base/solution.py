"""Choose pending tasks that can be dispatched next."""


def ready_tasks(tasks, capacity):
    done = {task["id"] for task in tasks if task.get("status", "pending") == "done"}
    ready = [task for task in tasks if task.get("status", "pending") == "pending" and all(dep in done for dep in task.get("depends_on", []))]
    ready.sort(key=lambda task: -task.get("priority", 0))
    return [task["id"] for task in ready[:capacity]]
