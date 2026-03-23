import json
import os

TASKS_FILE = "tasks.json"

def load_tasks():
    if os.path.exists(TASKS_FILE):
        with open(TASKS_FILE, "r") as f:
            return json.load(f)
    return []

def save_tasks(tasks):
    with open(TASKS_FILE, "w") as f:
        json.dump(tasks, f, indent=2)

def show_tasks(tasks):
    if not tasks:
        print("\n  No tasks yet. Add one!\n")
        return
    print("\n  YOUR TO-DO LIST")
    print("  " + "-" * 30)
    for i, task in enumerate(tasks, 1):
        status = "✓" if task["done"] else " "
        print(f"  [{status}] {i}. {task['name']}")
    print("  " + "-" * 30 + "\n")

def add_task(tasks):
    name = input("  Task name: ").strip()
    if name:
        tasks.append({"name": name, "done": False})
        save_tasks(tasks)
        print(f"  Added: '{name}'\n")
    else:
        print("  Task name cannot be empty.\n")

def complete_task(tasks):
    show_tasks(tasks)
    if not tasks:
        return
    try:
        num = int(input("  Enter task number to mark complete: "))
        task = tasks[num - 1]
        task["done"] = True
        save_tasks(tasks)
        print(f"  Marked done: '{task['name']}'\n")
    except (ValueError, IndexError):
        print("  Invalid number.\n")

def delete_task(tasks):
    show_tasks(tasks)
    if not tasks:
        return
    try:
        num = int(input("  Enter task number to delete: "))
        removed = tasks.pop(num - 1)
        save_tasks(tasks)
        print(f"  Deleted: '{removed['name']}'\n")
    except (ValueError, IndexError):
        print("  Invalid number.\n")

def main():
    tasks = load_tasks()
    print("\n  Welcome to your To-Do List!")

    while True:
        print("  What do you want to do?")
        print("  1. View tasks")
        print("  2. Add task")
        print("  3. Mark task complete")
        print("  4. Delete task")
        print("  5. Quit")

        choice = input("\n  Enter choice (1-5): ").strip()

        if choice == "1":
            show_tasks(tasks)
        elif choice == "2":
            add_task(tasks)
        elif choice == "3":
            complete_task(tasks)
        elif choice == "4":
            delete_task(tasks)
        elif choice == "5":
            print("\n  Bye!\n")
            break
        else:
            print("  Please enter a number between 1 and 5.\n")

if __name__ == "__main__":
    main()
