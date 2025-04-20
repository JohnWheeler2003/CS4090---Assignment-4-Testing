# Bug Reports

## Bug 1: New‑task IDs collide after deletion

**Environment:**
Streamlit app (`src/app.py`) on Python 3.10, WSL Ubuntu

**Description:**  
In `app.py`, new tasks are created with  
"id": len(tasks) + 1

**Steps to Reproduce:**

    Add Task A → ID 1

    Add Task B → ID 2

    Delete Task A (only Task B remains, ID 2)

    Add Task C → app assigns id = 2 again

**Expected Behavior** 
Each new task should receive a never‑used integer ID (e.g. 3), even after deletions.

**Actual Behavior:**
The code reuses ID 2, causing two tasks to share the same ID.

**Severity:**
Medium (duplicate IDs break delete/complete logic)

--- Before fix (in src/app.py) ---
-    new_task = {
-        "id": len(tasks) + 1,
-        "title": title,
-        "description": description,
-        "priority": priority,
-        "category": category,
-        "due_date": due_date,
-        "completed": False
-    }

+++ After fix (in src/app.py) +++
+from src.tasks import generate_unique_id
+
+    new_task = {
+        "id": generate_unique_id(tasks),
+        "title": title,
+        "description": description,
+        "priority": priority,
+        "category": category,
+        "due_date": due_date,
+        "completed": False
+    }

**Validation:**
    Added a pytest in tests/test_advanced.py:

        def test_generate_unique_id_after_deletion():
            tasks = [{"id": i} for i in (1, 2, 3)]
            tasks = [t for t in tasks if t["id"] != 2]
            assert generate_unique_id(tasks) == 4

    Running pytest --maxfail=1 -q shows 11 tests passing, including this new one.

    Coverage remains at 100% on src/tasks.py



## Bug 2: Tasks without due dates or with invalid date strings are flagged as overdue

**Environment:**
src/tasks.py on Python 3.10, WSL Ubuntu

**Description:**
The function get_overdue_tasks treats any task lacking a "due_date" (or having a malformed date string) as overdue, because it defaults to "" and compares "" < "YYYY‑MM‑DD" lexicographically.

**Steps to Reproduce:**

    1. Define

        tasks = [
        {"id": 1, "due_date": "",           "completed": False},
        {"id": 2, "due_date": "not‑a‑date", "completed": False},
        ]

    2.Call get_overdue_tasks(tasks)

    3. Both tasks are returned as overdue.

**Expected Behavior:**
Tasks without a due date or with invalid date formats should not appear in the overdue list.

**Actual Behavior:**
Both tasks show up as overdue.

**Severity:**
Low‑Medium (incorrect overdue listings can confuse users)

--- Before fix (src/tasks.py) ---
-def get_overdue_tasks(tasks):
-    today = datetime.now().strftime("%Y-%m-%d")
-    return [
-        task for task in tasks
-        if not task.get("completed", False) and
-           task.get("due_date", "") < today
-    ]

+++ After fix (src/tasks.py) +++
+def get_overdue_tasks(tasks):
+    """
+    Get tasks that are past their due date and not completed.
+
+    Only tasks with a valid YYYY‑MM‑DD due_date are considered.
+    """
+    today = datetime.now().date()
+    overdue = []
+    for task in tasks:
+        if task.get("completed", False):
+            continue
+        due_str = task.get("due_date", "")
+        if not due_str:
+            continue
+        try:
+            due_date = datetime.strptime(due_str, "%Y-%m-%d").date()
+        except (ValueError, TypeError):
+            # skip missing or malformed dates
+            continue
+        if due_date < today:
+            overdue.append(task)
+    return overdue

**Validation:**

    Added pytest cases in tests/test_advanced.py:

    import pytest
    from datetime import datetime as RealDateTime
    import src.tasks as tasks_mod

    def test_get_overdue_ignores_missing_due_date():
        tasks = [{"id": 1, "due_date": "", "completed": False}]
        assert tasks_mod.get_overdue_tasks(tasks) == []

    def test_get_overdue_ignores_invalid_date_format():
        tasks = [{"id": 2, "due_date": "foo-bar", "completed": False}]
        assert tasks_mod.get_overdue_tasks(tasks) == []

    def test_get_overdue_includes_only_past_dates(monkeypatch):
        class DummyDateTime(RealDateTime):
            @classmethod
            def now(cls):
                return cls(2025, 4, 19)
        monkeypatch.setattr(tasks_mod, 'datetime', DummyDateTime)
        tasks = [
            {"id": 3, "due_date": "2025-04-18", "completed": False},
            {"id": 4, "due_date": "2025-04-19", "completed": False},
            {"id": 5, "due_date": "2025-04-20", "completed": False},
        ]
        overdue = tasks_mod.get_overdue_tasks(tasks)
        assert [t["id"] for t in overdue] == [3]

    Running pytest --maxfail=1 -q now shows 14 tests passing.

    Coverage remains at 100% for src/tasks.py.


##Bug 3: Corrupted JSON files aren’t purged, leading to repeated warnings

**Environment**

src/tasks.py on Python 3.10, WSL Ubuntu

**Description**

When load_tasks() encounters invalid JSON, it prints a warning but does not clear or replace the bad file. On every subsequent app launch you’ll get the same warning and an empty task list, but the corrupt file remains.

**Steps to Reproduce**

    Manually write invalid text into tasks.json.

    Start the app → see “Warning: tasks.json contains invalid JSON. Creating new tasks list.”

    Close and restart the app → see the same warning again (file hasn’t been fixed), and no tasks.

**Expected Behavior**
After detecting corruption, the code should either (a) overwrite tasks.json with an empty list or (b) rename the bad file to something like tasks.json.bak and create a fresh tasks.json.
Actual Behavior

The file is left untouched, so every launch re‑raises the warning and never recovers.

**Severity**
Low‑Medium (poor user experience and persistent error state)

--- Before (in src/tasks.py) ---
 except json.JSONDecodeError:
-    # Handle corrupted JSON file
-    print(f"Warning: {file_path} contains invalid JSON. Creating new tasks list.")
-    return []

+++ After (in src/tasks.py) +++
+except json.JSONDecodeError:
+    # Handle corrupted JSON file: back it up and start fresh
+    backup = file_path + ".bak"
+    os.replace(file_path, backup)  # rename the bad file
+    print(f"Warning: {file_path} was invalid JSON. Backed up to {backup}. Starting fresh.")
+    save_tasks([], file_path)
+    return []

**Validation:**

In test_basic.py:
    def test_load_corrupted_json(tmp_path, capsys):
    file_path = tmp_path / "tasks.json"
    file_path.write_text("not json")
    result = load_tasks(str(file_path))
    captured = capsys.readouterr()
    # confirm new warning and backup message
    assert "was invalid JSON" in captured.out
    assert "Backed up to" in captured.out
    # still returns empty list
    assert result == []

In test_advanced.py:
    def test_load_corrupted_json_backs_up(tmp_path, capsys):
    bad = tmp_path / "tasks.json"
    bad.write_text("<<<not json>>>")

    # import the module under test
    from src import tasks as tasks_mod

    # Call load_tasks with our bad file’s path
    result = tasks_mod.load_tasks(str(bad))

    # The corrupted file should have been renamed to .bak
    bak = tmp_path / "tasks.json.bak"
    assert bak.exists(), f"Expected backup at {bak}"

    # And a fresh, empty tasks.json should have been written
    new_file = tmp_path / "tasks.json"
    assert new_file.exists(), f"Expected new file at {new_file}"
    fresh = json.loads(new_file.read_text())
    assert fresh == []

    # Confirm the backup message was printed
    captured = capsys.readouterr()
    assert "Backed up to" in captured.out

