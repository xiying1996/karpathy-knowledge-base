import logging
import time
from pathlib import Path
from threading import Lock
from typing import Callable

from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer
from watchdog.observers.polling import PollingObserver

logger = logging.getLogger(__name__)


class DebouncedHandler(FileSystemEventHandler):
    def __init__(self, callback: Callable[[str, str], None], debounce: float = 2.0):
        self.callback = callback
        self.debounce = debounce
        self._lock = Lock()
        self._pending: dict[str, float] = {}

    def _should_process(self, path: str) -> bool:
        with self._lock:
            now = time.time()
            last_time = self._pending.get(path, 0)
            if now - last_time < self.debounce:
                logger.warning(f"[FileWatcher] Debouncing {path}, waiting {self.debounce}s...")
                return False
            self._pending[path] = now
            return True

    def on_created(self, event: FileSystemEvent):
        if event.is_directory or not event.src_path.endswith(".md"):
            return
        if self._should_process(event.src_path):
            logger.info(f"[FileWatcher] Detected: CREATE {event.src_path}")
            self.callback("CREATE", event.src_path)

    def on_modified(self, event: FileSystemEvent):
        if event.is_directory or not event.src_path.endswith(".md"):
            return
        if self._should_process(event.src_path):
            logger.info(f"[FileWatcher] Detected: MODIFY {event.src_path}")
            self.callback("MODIFY", event.src_path)

    def on_deleted(self, event: FileSystemEvent):
        if event.is_directory or not event.src_path.endswith(".md"):
            return
        logger.info(f"[FileWatcher] Detected: DELETE {event.src_path}")
        self.callback("DELETE", event.src_path)


class FileWatcher:
    def __init__(
        self,
        vault_path: str,
        mode: str = "watch",
        poll_interval: int = 2,
        debounce: int = 2,
        on_change: Callable[[str, str], None] | None = None,
    ):
        self.vault_path = Path(vault_path)
        self.mode = mode
        self.poll_interval = poll_interval
        self.debounce = debounce
        self.on_change = on_change or (lambda event_type, path: None)
        self._observer: Observer | PollingObserver | None = None

    def start(self):
        handler = DebouncedHandler(self.on_change, debounce=self.debounce)
        if self.mode == "poll":
            self._observer = PollingObserver(timeout=self.poll_interval)
        else:
            self._observer = Observer()
        self._observer.schedule(handler, str(self.vault_path), recursive=True)
        self._observer.start()
        logger.info(f"[FileWatcher] Started watching: {self.vault_path}, mode={self.mode}")

    def stop(self):
        if self._observer:
            self._observer.stop()
            self._observer.join()
            logger.info("[FileWatcher] Stopped")

    def is_alive(self) -> bool:
        return self._observer is not None and self._observer.is_alive()