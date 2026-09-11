from models import AuditLogs


def record(db, inspection_id: str, user_id: str | None, action: str, target: str = None,
           old_value=None, new_value=None, source: str = "INSPECTOR"):
    entry = AuditLogs(
        inspection_id=inspection_id,
        user_id=user_id,
        action=action,
        target=target,
        old_value=old_value,
        new_value=new_value,
        source=source,
    )
    db.add(entry)
    return entry


def history(db, inspection_id: str):
    return (
        db.query(AuditLogs)
        .filter(AuditLogs.inspection_id == inspection_id)
        .order_by(AuditLogs.created_at)
        .all()
    )
