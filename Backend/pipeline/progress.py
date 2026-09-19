import asyncio
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)

# Ordered stages the pipeline moves through, so the client can render a
# checklist. The route adds the terminal "done"/"failed" events itself.
STAGES = [
    {"key": "ocr", "label": "Reading the label with OCR"},
    {"key": "extraction", "label": "Extracting declarations"},
    {"key": "measurement", "label": "Measuring font sizes"},
    {"key": "compliance", "label": "Running the rule engine"},
]


class ProgressHub:
    """Minimal in-process pub/sub so the synchronous pipeline (which FastAPI
    runs in a worker thread) can stream stage updates to WebSocket clients
    watching a single inspection."""

    def __init__(self):
        self._subscribers: dict[str, set[asyncio.Queue]] = defaultdict(set)
        self._loop: asyncio.AbstractEventLoop | None = None

    def bind_loop(self, loop: asyncio.AbstractEventLoop):
        self._loop = loop

    def subscribe(self, inspection_id: str) -> asyncio.Queue:
        queue: asyncio.Queue = asyncio.Queue()
        self._subscribers[inspection_id].add(queue)
        return queue

    def unsubscribe(self, inspection_id: str, queue: asyncio.Queue):
        watchers = self._subscribers.get(inspection_id)
        if watchers:
            watchers.discard(queue)
            if not watchers:
                self._subscribers.pop(inspection_id, None)

    def publish(self, inspection_id: str, event: dict):
        """Safe to call from any thread - the pipeline runs off the event loop."""
        watchers = self._subscribers.get(inspection_id)
        if not watchers or self._loop is None:
            return
        for queue in list(watchers):
            self._loop.call_soon_threadsafe(queue.put_nowait, event)


hub = ProgressHub()


def publish(inspection_id: str, stage: str, status: str = "running", detail: str | None = None):
    hub.publish(inspection_id, {"stage": stage, "status": status, "detail": detail})
