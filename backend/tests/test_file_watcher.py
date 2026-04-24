import time
from pathlib import Path
from unittest.mock import MagicMock

from app.services.file_watcher import FileWatcher, DebouncedHandler


def make_mock_event(event_type: str, src_path: str | Path, is_directory: bool = False):
    event = MagicMock()
    event.is_directory = is_directory
    event.src_path = str(src_path)
    event.event_type = event_type
    return event


def test_debounced_handler_on_created():
    events = []
    handler = DebouncedHandler(lambda et, p: events.append((et, p)), debounce=0.1)

    event = make_mock_event("created", "/tmp/test.md")
    handler.on_created(event)
    time.sleep(0.15)
    event2 = make_mock_event("created", "/tmp/test2.md")
    handler.on_created(event2)

    assert len(events) == 2
    assert events[0] == ("CREATE", "/tmp/test.md")


def test_debounced_handler_ignores_non_md():
    events = []
    handler = DebouncedHandler(lambda et, p: events.append((et, p)), debounce=0.1)

    event = make_mock_event("created", "/tmp/test.txt")
    handler.on_created(event)

    assert len(events) == 0


def test_debounced_handler_ignores_directories():
    events = []
    handler = DebouncedHandler(lambda et, p: events.append((et, p)), debounce=0.1)

    event = make_mock_event("created", "/tmp/subdir", is_directory=True)
    handler.on_created(event)

    assert len(events) == 0


def test_debounced_handler_modify():
    events = []
    handler = DebouncedHandler(lambda et, p: events.append((et, p)), debounce=0.1)

    event = make_mock_event("modified", "/tmp/test.md")
    handler.on_modified(event)

    assert len(events) == 1
    assert events[0][0] == "MODIFY"


def test_debounced_handler_delete():
    events = []
    handler = DebouncedHandler(lambda et, p: events.append((et, p)), debounce=0.1)

    event = make_mock_event("deleted", "/tmp/test.md")
    handler.on_deleted(event)

    assert len(events) == 1
    assert events[0][0] == "DELETE"


def test_file_watcher_start_stop():
    watcher = FileWatcher(
        vault_path="/tmp",
        mode="watch",
        debounce=1,
    )
    assert not watcher.is_alive()
    watcher.start()
    assert watcher.is_alive()
    watcher.stop()
    assert not watcher.is_alive()


def test_file_watcher_poll_mode():
    watcher = FileWatcher(
        vault_path="/tmp",
        mode="poll",
        poll_interval=1,
        debounce=1,
    )
    watcher.start()
    assert watcher.is_alive()
    watcher.stop()


def test_file_watcher_on_change_callback(tmp_path):
    calls = []
    watcher = FileWatcher(
        vault_path=str(tmp_path),
        mode="watch",
        debounce=0.1,
        on_change=lambda et, p: calls.append((et, p)),
    )
    watcher.start()
    time.sleep(0.2)

    test_file = tmp_path / "callbacks.md"
    test_file.write_text("# Callback Test")

    time.sleep(0.3)
    watcher.stop()

    assert len(calls) >= 1