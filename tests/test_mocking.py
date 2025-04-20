# tests/test_mocking.py
import pytest
import builtins
from src import tasks as tasks_mod

def test_save_tasks_io_error(monkeypatch, tmp_path):
    """
    If saving tasks fails with an IOError (e.g. disk full),
    save_tasks should propagate that error.
    """
    path = tmp_path / "tasks.json"

    # Monkey‑patch builtins.open so any open() raises IOError
    def fake_open(*args, **kwargs):
        raise IOError("disk full")
    monkeypatch.setattr(builtins, 'open', fake_open)

    with pytest.raises(IOError) as excinfo:
        tasks_mod.save_tasks([{'id': 1}], str(path))
    assert "disk full" in str(excinfo.value)


def test_load_tasks_permission_error(monkeypatch):
    """
    If loading tasks hits a PermissionError (e.g. cannot read file),
    load_tasks should propagate that exception.
    """
    # Monkey‑patch builtins.open so any open() raises PermissionError
    def fake_open(*args, **kwargs):
        raise PermissionError("permission denied")
    monkeypatch.setattr(builtins, 'open', fake_open)

    with pytest.raises(PermissionError):
        tasks_mod.load_tasks("irrelevant.json")
