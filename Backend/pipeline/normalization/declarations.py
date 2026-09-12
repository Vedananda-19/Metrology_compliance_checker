from pipeline.extraction.declarations import FIELDS


def normalize(extracted) -> dict:
    values = {}
    for field in FIELDS:
        declared = getattr(extracted, field, None)
        if declared is None:
            continue
        value = (declared.value or "").strip()
        if not value:
            continue
        values[field] = {"value": value, "confidence": round(float(declared.confidence or 0.0), 3)}
    return values


def present(values: dict) -> list[str]:
    return sorted(values)


def missing(values: dict) -> list[str]:
    return sorted(field for field in FIELDS if field not in values)


def as_text(values: dict) -> str:
    lines = [f"- {FIELDS[field]}: {item['value']}" for field, item in sorted(values.items())]
    absent = [f"- {FIELDS[field]}: not found on any uploaded panel" for field in missing(values)]
    return "\n".join(lines + absent)
