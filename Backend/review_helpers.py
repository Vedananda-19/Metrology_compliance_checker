from sqlalchemy import func
from models import RuleResults


def next_run_no(db, inspection_id: str) -> int:
    value = db.query(func.max(RuleResults.run_no)).filter(
        RuleResults.inspection_id == inspection_id
    ).scalar()
    return (value or 0) + 1
