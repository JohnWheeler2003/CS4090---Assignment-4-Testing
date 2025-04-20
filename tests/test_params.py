# tests/test_params.py
import pytest
from src.tasks import (
    filter_tasks_by_priority,
    filter_tasks_by_completion,
    filter_tasks_by_category,
    search_tasks,
)

@pytest.mark.parametrize(
    "tasks, priority, expected_ids",
    [
        ([], "High", []),
        ([{"id": 1, "priority": "High"}], "High", [1]),
        ([{"id": 2, "priority": "Low"}], "High", []),
        ([{"id": 3, "priority": "Low"}, {"id": 4, "priority": "Low"}], "Low", [3, 4]),
    ],
)
def test_filter_tasks_by_priority(tasks, priority, expected_ids):
    result = filter_tasks_by_priority(tasks, priority)
    assert [t["id"] for t in result] == expected_ids


@pytest.mark.parametrize(
    "tasks, completed, expected_ids",
    [
        ([], True, []),
        ([{"id": 1, "completed": True}], True, [1]),
        ([{"id": 2, "completed": False}], True, []),
        ([{"id": 3, "completed": False}, {"id": 4, "completed": False}], False, [3, 4]),
    ],
)
def test_filter_tasks_by_completion(tasks, completed, expected_ids):
    result = filter_tasks_by_completion(tasks, completed)
    assert [t["id"] for t in result] == expected_ids


@pytest.mark.parametrize(
    "tasks, category, expected_ids",
    [
        ([], "Work", []),
        ([{"id": 1, "category": "Work"}], "Work", [1]),
        ([{"id": 2, "category": "Home"}], "Work", []),
        (
            [
                {"id": 3, "category": "Home"},
                {"id": 4, "category": "Work"},
                {"id": 5, "category": "Work"},
            ],
            "Work",
            [4, 5],
        ),
    ],
)
def test_filter_tasks_by_category(tasks, category, expected_ids):
    result = filter_tasks_by_category(tasks, category)
    assert [t["id"] for t in result] == expected_ids


@pytest.mark.parametrize(
    "tasks, query, expected_ids",
    [
        ([], "anything", []),
        ([{"id": 1, "title": "Buy milk", "description": ""}], "buy", [1]),
        ([{"id": 2, "title": "Read", "description": "science book"}], "science", [2]),
        (
            [
                {"id": 3, "title": "Walk dog", "description": ""},
                {"id": 4, "title": "Dog food", "description": "buy more"},
            ],
            "dog",
            [3, 4],
        ),
        (
            [{"id": 5, "title": "Test", "description": "Case"}],
            "xyz",
            [],
        ),
    ],
)
def test_search_tasks_param(tasks, query, expected_ids):
    result = search_tasks(tasks, query)
    assert [t["id"] for t in result] == expected_ids
