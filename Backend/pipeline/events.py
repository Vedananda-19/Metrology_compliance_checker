import asyncio
from datetime import datetime, timezone

STEPS = [
    "IMAGE_RECEIVED",
    "PREPROCESSING",
    "OCR",
    "DECLARATION_EXTRACTION",
    "PRODUCT_CLASSIFICATION",
    "RULE_IDENTIFICATION",
    "COMPLIANCE_ANALYSIS",
    "EVIDENCE_GENERATION",
    "REPORT_GENERATION",
]

_queues: dict[str, asyncio.Queue] = {}


def make_event(step: str, status: str, message: str, **extra):
    event = {
        "step": step,
        "status": status,
        "message": message,
        "at": datetime.now(timezone.utc).isoformat(),
    }
    event.update(extra)
    return event


def queue_for(inspection_id: str) -> asyncio.Queue:
    queue = _queues.get(inspection_id)
    if queue is None:
        queue = asyncio.Queue()
        _queues[inspection_id] = queue
    return queue


def has_queue(inspection_id: str) -> bool:
    return inspection_id in _queues


def publish(inspection_id: str, event: dict):
    queue = _queues.get(inspection_id)
    if queue is not None:
        queue.put_nowait(event)


def close(inspection_id: str):
    queue = _queues.get(inspection_id)
    if queue is not None:
        queue.put_nowait(None)


def discard(inspection_id: str):
    _queues.pop(inspection_id, None)


class Reporter:
    def __init__(self, inspection_id: str, log: list):
        self.inspection_id = inspection_id
        self.log = log

    def emit(self, step: str, status: str, message: str, **extra):
        event = make_event(step, status, message, **extra)
        self.log.append(event)
        publish(self.inspection_id, event)
        return event

    def started(self, step: str, message: str, **extra):
        return self.emit(step, "processing", message, **extra)

    def completed(self, step: str, message: str, **extra):
        return self.emit(step, "completed", message, **extra)

    def failed(self, step: str, message: str, **extra):
        return self.emit(step, "failed", message, **extra)
