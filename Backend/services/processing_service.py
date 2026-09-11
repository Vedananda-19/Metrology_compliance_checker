from fastapi import HTTPException
from sqlalchemy.orm.attributes import flag_modified
from database import SessionLocal
from models import Inspections
from services import inspection_service, audit_service
from pipeline import events, fallback
from pipeline.graph import Pipeline
from engine import engine as rule_engine
from pipeline import facts as fact_builder
import asyncio
import logging

logger = logging.getLogger(__name__)

_pipeline = Pipeline()


def get_pipeline() -> Pipeline:
    return _pipeline


def start(inspection_id: str, db, user):
    inspection = inspection_service.get_owned(db, inspection_id, user.user_id)
    inspection_service.assert_not_finalized(inspection)

    usable = inspection_service.usable_images(db, inspection_id)
    if not usable:
        raise HTTPException(400, "Mark at least one image usable before processing")
    if inspection.status == "PROCESSING":
        raise HTTPException(409, "This inspection is already being processed")

    inspection.status = "PROCESSING"
    inspection.processing_log = []
    inspection.processing_error = None
    audit_service.record(db, inspection.id, user.user_id, "processing_started")
    db.commit()

    events.queue_for(inspection_id)
    asyncio.get_running_loop().create_task(asyncio.to_thread(execute, inspection_id, user.user_id))
    return {"message": "Processing started", "inspection_id": inspection_id}


def reevaluator(pipeline: Pipeline, db, inspection: Inspections, state: dict):
    def rerun():
        product = inspection_service.get_product(db, inspection.id)
        raw_facts = fact_builder.build(db, inspection, product)
        report = rule_engine.run(
            raw_facts,
            on_date=inspection.judged_as_of,
            ruleset=state.get("ruleset"),
            tables=state.get("tables"),
        )
        state["run_no"] = state.get("run_no", 1) + 1
        pipeline.db = db
        pipeline.store_results(inspection, report, state["run_no"])
        pipeline.generate_evidence({"inspection_id": inspection.id})
        state["report"] = report
        return report

    return rerun


def execute(inspection_id: str, user_id: str):
    db = SessionLocal()
    pipeline = get_pipeline()
    try:
        inspection = db.query(Inspections).filter(Inspections.id == inspection_id).first()
        if inspection is None:
            return

        log = []
        reporter = events.Reporter(inspection_id, log)
        state = pipeline.run(db, inspection, reporter, run_no=1)

        if not state.get("degraded_mode") and not state.get("error"):
            try:
                pipeline.db = db
                pipeline.reporter = reporter
                fallback.run(db, inspection, state, reporter, reevaluator(pipeline, db, inspection, state))
            except Exception:
                logger.exception("LLM fallback failed")
                reporter.emit("COMPLIANCE_ANALYSIS", "completed", "Advisory step skipped after an error")

        inspection = db.query(Inspections).filter(Inspections.id == inspection_id).first()
        inspection.processing_log = log
        flag_modified(inspection, "processing_log")

        if state.get("error") and not state.get("report"):
            inspection.status = "IMAGE_REVIEW"
            inspection.processing_error = state["error"]
        else:
            inspection.status = "EXTRACTION_REVIEW"

        audit_service.record(
            db, inspection.id, user_id, "processing_completed", None, None,
            {"verdict": inspection.automated_verdict, "degraded": bool(state.get("degraded_mode"))},
        )
        db.commit()
        events.publish(inspection_id, events.make_event("REPORT_GENERATION", "completed", "Processing finished", done=True))
    except Exception as error:
        logger.exception("Processing failed for %s", inspection_id)
        db.rollback()
        inspection = db.query(Inspections).filter(Inspections.id == inspection_id).first()
        if inspection is not None:
            inspection.status = "IMAGE_REVIEW"
            inspection.processing_error = str(error)
            db.commit()
        events.publish(inspection_id, events.make_event("REPORT_GENERATION", "failed", str(error), done=True))
    finally:
        events.close(inspection_id)
        db.close()


async def stream(inspection_id: str, db, user):
    inspection = inspection_service.get_owned(db, inspection_id, user.user_id)
    queue = events.queue_for(inspection_id)
    replay = list(inspection.processing_log or [])
    status = inspection.status
    db.close()

    async def generator():
        import json

        for event in replay:
            yield f"data: {json.dumps(event)}\n\n"

        if status != "PROCESSING":
            yield f"data: {json.dumps(events.make_event('REPORT_GENERATION', 'completed', 'Processing already finished', done=True))}\n\n"
            return

        try:
            while True:
                event = await asyncio.wait_for(queue.get(), timeout=180)
                if event is None:
                    break
                yield f"data: {json.dumps(event)}\n\n"
                if event.get("done"):
                    break
        except asyncio.TimeoutError:
            yield f"data: {json.dumps(events.make_event('REPORT_GENERATION', 'failed', 'Processing timed out', done=True))}\n\n"
        finally:
            events.discard(inspection_id)

    return generator()
