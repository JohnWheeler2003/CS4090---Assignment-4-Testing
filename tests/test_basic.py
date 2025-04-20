# tests/test_basic.py
import pytest
import json
from src.tasks import (
    generate_unique_id,
    filter_tasks_by_priority,
    filter_tasks_by_category,
    filter_tasks_by_completion,
    search_tasks,
    get_overdue_tasks,
    load_tasks,
    save_tasks
)

def test_generate_unique_id_empty():
    assert generate_unique_id([]) == 1

def test_generate_unique_id_non_empty():
    tasks = [{"id": 1}, {"id": 3}, {"id": 2}]
    assert generate_unique_id(tasks) == 4

def test_filter_tasks_by_priority():
    tasks = [
        {"id": 1, "priority": "High"},
        {"id": 2, "priority": "Low"},
        {"id": 3, "priority": "High"}
    ]
    high = filter_tasks_by_priority(tasks, "High")
    assert [t["id"] for t in high] == [1, 3]

def test_filter_tasks_by_completion():
    tasks = [{"id": 1, "completed": True}, {"id": 2, "completed": False}]
    completed = filter_tasks_by_completion(tasks, True)
    assert [t["id"] for t in completed] == [1]

def test_search_tasks():
    tasks = [
        {"id": 1, "title": "Buy milk", "description": ""},
        {"id": 2, "title": "Homework", "description": "math assignment"}
    ]
    assert search_tasks(tasks, "milk") == [tasks[0]]
    assert search_tasks(tasks, "math") == [tasks[1]]
    assert search_tasks(tasks, "xyz") == []

def test_get_overdue_tasks():
    tasks = [
        {"id": 1, "due_date": "2000-01-01", "completed": False},
        {"id": 2, "due_date": "3000-01-01", "completed": False},
        {"id": 3, "due_date": "2000-01-01", "completed": True}
    ]
    overdue = get_overdue_tasks(tasks)
    assert [t["id"] for t in overdue] == [1]

def test_save_and_load_tasks(tmp_path):
    file_path = tmp_path / "tasks.json"
    tasks = [{"id": 1, "title": "A"}]
    save_tasks(tasks, str(file_path))
    loaded = load_tasks(str(file_path))
    assert loaded == tasks

def test_load_nonexistent(tmp_path):
    file_path = tmp_path / "no.json"
    assert load_tasks(str(file_path)) == []

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


def test_filter_tasks_by_category():
    tasks = [
        {"id": 1, "category": "Work"},
        {"id": 2, "category": "Personal"},
        {"id": 3, "category": "Work"},
        {"id": 4}  # no category key
    ]
    work = filter_tasks_by_category(tasks, "Work")
    assert [t["id"] for t in work] == [1, 3]
