import pytest
import tempfile, json
from src.tasks import generate_unique_id
import src.tasks as tasks_mod
from datetime import datetime as RealDateTime

def test_generate_unique_id_after_deletion():
    # simulate tasks 1,2,3
    tasks = [{"id": i} for i in (1,2,3)]
    # delete ID 2
    tasks = [t for t in tasks if t["id"] != 2]
    # next ID should jump to 4, not re‑use 2
    assert generate_unique_id(tasks) == 4

def test_get_overdue_ignores_missing_due_date():
    tasks = [{"id": 1, "due_date": "", "completed": False}]
    assert tasks_mod.get_overdue_tasks(tasks) == []

def test_get_overdue_ignores_invalid_date_format():
    tasks = [{"id": 2, "due_date": "foo-bar", "completed": False}]
    assert tasks_mod.get_overdue_tasks(tasks) == []

def test_get_overdue_includes_only_past_dates(monkeypatch):
    # Create a dummy datetime class that inherits from real datetime
    class DummyDateTime(RealDateTime):
        @classmethod
        def now(cls):
            # Freeze 'today' as April 19, 2025
            return cls(2025, 4, 19)

    # Monkey‐patch the datetime in tasks_mod to our DummyDateTime
    monkeypatch.setattr(tasks_mod, 'datetime', DummyDateTime)

    tasks = [
        {"id": 3, "due_date": "2025-04-18", "completed": False},
        {"id": 4, "due_date": "2025-04-19", "completed": False},
        {"id": 5, "due_date": "2025-04-20", "completed": False},
    ]
    overdue = tasks_mod.get_overdue_tasks(tasks)
    assert [t["id"] for t in overdue] == [3]


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

