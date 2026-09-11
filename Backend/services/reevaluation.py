from services import processing_service, inspection_service
from pipeline import facts as fact_builder
from pipeline.graph import load_rule_data
from engine import engine as rule_engine
from review_helpers import next_run_no


def reevaluate(db, inspection):
    ruleset, tables = load_rule_data(db, inspection.rule_set_version)
    product = inspection_service.get_product(db, inspection.id)
    raw_facts = fact_builder.build(db, inspection, product)
    report = rule_engine.run(
        raw_facts,
        on_date=inspection.judged_as_of,
        ruleset=ruleset,
        tables=tables,
    )

    pipeline = processing_service.get_pipeline()
    pipeline.db = db
    pipeline.reporter = None
    run_no = next_run_no(db, inspection.id)
    pipeline.store_results(inspection, report, run_no)
    pipeline.generate_evidence({"inspection_id": inspection.id, "degraded_mode": False})
    db.flush()
    return report
