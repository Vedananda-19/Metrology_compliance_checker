"""
Reference rule interpreter for the LMPC rule set.

    python engine.py ../samples/biscuits_domestic.json
    python engine.py ../samples/salt_450g.json --date 2012-01-15
    python engine.py <facts.json> --include-drafts --json

The engine knows NOTHING about Legal Metrology. It knows:
  * three-valued logic (TRUE / FALSE / UNKNOWN)
  * a small set of generic operators (eq, in, regex, gte ...)
  * a small library of named domain operators ("fn") that do table lookups and unit maths
Everything legal lives in rules/lmpc_2011_rules.json and rules/reference_tables.json.
"""
from __future__ import annotations

import argparse
import json
import math
import re
import sys
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

T, F, U = "TRUE", "FALSE", "UNKNOWN"
ROOT = Path(__file__).resolve().parent
RULES_DIR = ROOT / "rules"
AUTOMATED_MODES = {"LABEL_AUTOMATED", "VISION_AUTOMATED"}


def load_ruleset():
    return json.loads((RULES_DIR / "lmpc_2011_rules.json").read_text(encoding="utf-8"))


def load_tables():
    return json.loads((RULES_DIR / "reference_tables.json").read_text(encoding="utf-8"))


# --------------------------------------------------------------------------- three-valued logic
def k_and(vals):
    vals = list(vals)
    if F in vals: return F
    if U in vals: return U
    return T

def k_or(vals):
    vals = list(vals)
    if T in vals: return T
    if U in vals: return U
    return F

def k_not(v):
    return {T: F, F: T, U: U}[v]

def tv(b: bool) -> str:
    return T if b else F


# --------------------------------------------------------------------------- facts
@dataclass
class Fact:
    path: str
    present: bool
    value: object = None
    confidence: float = 1.0
    evidence: object = None
    source: str = "AI"


class FactStore:
    """Flat fact map: {"mrp.value": {"value": 40, "confidence": 0.98, "evidence": {...}}, ...}.
    A bare value is treated as officer-provided context with confidence 1.0.
    If verification_status == VERIFIED the human_value wins (AI value kept for audit)."""

    def __init__(self, raw: dict, tables: dict):
        self.raw = {}
        for k, v in raw.items():
            if isinstance(v, dict) and ("value" in v or "human_value" in v):
                self.raw[k] = v
            else:
                self.raw[k] = {"value": v, "confidence": 1.0, "source": "CONTEXT"}
        self.tables = tables
        self._derive()

    def get(self, path: str) -> Fact:
        node = self.raw.get(path)
        if node is None:
            children = {k: v for k, v in self.raw.items() if k.startswith(path + ".")}
            if not children:
                return Fact(path, False)
            conf = min(self._conf(v) for v in children.values())
            val = {k[len(path) + 1:]: self._val(v) for k, v in children.items()}
            ev = [v.get("evidence") for v in children.values() if v.get("evidence")]
            return Fact(path, True, val, conf, ev or None, "AI")
        val = self._val(node)
        if val is None or val == "" or val == []:
            return Fact(path, False, confidence=self._conf(node), evidence=node.get("evidence"))
        return Fact(path, True, val, self._conf(node), node.get("evidence"),
                    "HUMAN" if node.get("verification_status") == "VERIFIED" else node.get("source", "AI"))

    @staticmethod
    def _val(node):
        if node.get("verification_status") == "VERIFIED" and "human_value" in node:
            return node["human_value"]
        return node.get("value")

    @staticmethod
    def _conf(node):
        if node.get("verification_status") == "VERIFIED":
            return 1.0
        return float(node.get("confidence", 1.0))

    def _derive(self):
        """net_quantity.dimension / base_value from value + unit (declared in rule set as DERIVED)."""
        if "net_quantity.base_value" in self.raw:
            return
        v, u = self.get("net_quantity.value"), self.get("net_quantity.unit")
        if not (v.present and u.present):
            return
        unit = canonical_unit(str(u.value), self.tables)
        if unit is None:
            return
        factor, dim = self.tables["units"]["to_base"][unit]
        conf = min(v.confidence, u.confidence)
        ev = v.evidence
        self.raw["net_quantity.dimension"] = {"value": dim, "confidence": conf, "evidence": ev, "source": "DERIVED"}
        self.raw["net_quantity.base_value"] = {"value": float(v.value) * factor, "confidence": conf, "evidence": ev, "source": "DERIVED"}
        self.raw["net_quantity.canonical_unit"] = {"value": unit, "confidence": conf, "evidence": ev, "source": "DERIVED"}


def canonical_unit(u: str, tables) -> str | None:
    u = u.strip().rstrip(".")
    for canon, aliases in tables["units"]["si_unit_aliases"].items():
        if canon == "count_2011":
            if u in aliases: return u
            continue
        if u in aliases or u.lower() in [a.lower() for a in aliases if a not in ("L", "mL")]:
            return canon
    return None


# --------------------------------------------------------------------------- evaluation context
@dataclass
class Ctx:
    facts: FactStore
    ruleset: dict
    tables: dict
    on_date: date
    phase: str = "check"            # applicability | exemption | check
    mode: str = "LABEL_AUTOMATED"
    used: dict = field(default_factory=dict)
    missing: set = field(default_factory=set)
    low_conf: set = field(default_factory=set)
    assumptions: list = field(default_factory=list)
    notes: list = field(default_factory=list)
    item: dict | None = None

    @property
    def policy(self):
        return self.tables["engineering_policy"]

    def coverage_complete(self) -> bool:
        c = self.facts.get("extraction.coverage_complete")
        return bool(c.present and c.value is True)

    def fact(self, path: str) -> Fact:
        if path.startswith("$item."):
            key = path[6:]
            val = (self.item or {}).get(key)
            return Fact(path, val not in (None, "", []), val, 1.0)
        fct = self.facts.get(path)
        if fct.present:
            self.used[path] = fct
        return fct


def resolve_value(v, ctx: Ctx):
    if isinstance(v, dict) and "policy" in v:
        return ctx.policy[v["policy"]]
    return v


# --------------------------------------------------------------------------- generic operators
def apply_op(op: str, actual, expected) -> str:
    try:
        if op == "exists": return T
        if op == "eq": return tv(actual == expected)
        if op == "ne": return tv(actual != expected)
        if op == "in": return tv(actual in expected)
        if op == "not_in": return tv(actual not in expected)
        if op == "contains": return tv(expected in actual)
        if op == "contains_any": return tv(any(e in actual for e in expected))
        if op == "matches_regex": return tv(re.search(expected, str(actual)) is not None)
        if op == "gt": return tv(float(actual) > float(expected))
        if op == "gte": return tv(float(actual) >= float(expected))
        if op == "lt": return tv(float(actual) < float(expected))
        if op == "lte": return tv(float(actual) <= float(expected))
        if op == "between": return tv(float(expected[0]) <= float(actual) <= float(expected[1]))
    except (TypeError, ValueError):
        return U
    raise ValueError(f"unknown operator {op}")


def evaluate(cond, ctx: Ctx) -> str:
    if "all" in cond: return k_and(evaluate(c, ctx) for c in cond["all"])
    if "any" in cond: return k_or([evaluate(c, ctx) for c in cond["any"]])
    if "not" in cond: return k_not(evaluate(cond["not"], ctx))
    if "macro" in cond: return evaluate(ctx.ruleset["macros"][cond["macro"]]["condition"], ctx)
    if "fn" in cond: return FUNCTIONS[cond["fn"]](ctx, **cond.get("args", {}))
    if "each" in cond:
        arr = ctx.fact(cond["each"])
        if not arr.present:
            return missing_result(cond["each"], "exists", ctx)
        results = []
        for item in arr.value:
            sub = Ctx(**{**ctx.__dict__, "item": item})
            results.append(evaluate(cond["require"], sub))
        return confidence_gate(k_and(results), arr, ctx)
    return evaluate_leaf(cond, ctx)


def evaluate_leaf(leaf, ctx: Ctx) -> str:
    path, op = leaf["fact"], leaf["op"]
    fct = ctx.fact(path)
    if not fct.present:
        if "absent_as" in leaf:
            ctx.assumptions.append(f"{path} not provided -> assumed condition '{op} {leaf.get('value')}' is {leaf['absent_as']}")
            return tv(bool(leaf["absent_as"]))
        return missing_result(path, op, ctx)
    return confidence_gate(apply_op(op, fct.value, resolve_value(leaf.get("value"), ctx)), fct, ctx)


def missing_result(path, op, ctx: Ctx) -> str:
    ctx.missing.add(path)
    if ctx.phase in ("applicability", "exemption"):
        return F if op == "exists" else U
    if ctx.mode in AUTOMATED_MODES and ctx.coverage_complete() and op in ("exists", "matches_regex"):
        return F          # a DECLARATION adequately looked for and still absent -> treat as absent
    # analysis signals (contrast, tamper, layout flags) that were never produced stay UNKNOWN
    return U              # "AI could not detect it" != "it does not exist"


def confidence_gate(result: str, fct: Fact, ctx: Ctx) -> str:
    if fct.path.startswith("$item."):
        return result
    if fct.confidence < ctx.policy["min_extraction_confidence"]:
        ctx.low_conf.add(fct.path)
        return U
    return result


# --------------------------------------------------------------------------- domain operators (fn)
def _get(ctx, path):
    f_ = ctx.fact(path)
    if not f_.present:
        ctx.missing.add(path)
        return None, U
    if f_.confidence < ctx.policy["min_extraction_confidence"]:
        ctx.low_conf.add(path)
        return f_.value, U
    return f_.value, T


def _tags(ctx):
    tags, st = _get(ctx, "product.tags")
    return (tags or []), st


def _dated(entries, on_date):
    out = []
    for e in entries:
        lo = date.fromisoformat(e.get("effective_from", "1900-01-01"))
        hi = date.fromisoformat(e["effective_to"]) if e.get("effective_to") else date.max
        if lo <= on_date <= hi:
            out.append(e)
    return out


def fn_is_second_schedule_commodity(ctx):
    tags, st = _tags(ctx)
    if st == U: return U
    return tv(any(t in ctx.tables["second_schedule_standard_sizes"]["commodities"] for t in tags))


def fn_standard_pack_size_ok(ctx):
    tags, st = _tags(ctx)
    qty, sq = _get(ctx, "net_quantity.base_value")
    if U in (st, sq): return U
    sched = ctx.tables["second_schedule_standard_sizes"]["commodities"]
    key = next(t for t in tags if t in sched)
    e = sched[key]
    q = round(qty, 3)
    if e.get("below_no_restriction") and q < e["below_no_restriction"]: return T
    if e.get("below_first_explicit_multiples_of") and q < e["explicit"][0]:
        return tv(math.isclose(q % e["below_first_explicit_multiples_of"], 0, abs_tol=1e-6))
    if e.get("above_no_restriction") and q > e["above_no_restriction"]: return T
    if q in e["explicit"]:
        cond = (e.get("conditional_sizes") or {}).get(str(int(q)) if q.is_integer() else str(q))
        if cond and cond not in tags:
            ctx.notes.append(f"{int(q)} is standard only for '{cond}'")
            return F
        return T
    m = e.get("thereafter_multiples_of")
    if m and q > max(e["explicit"]) and math.isclose(q % m, 0, abs_tol=1e-6):
        return tv(e.get("multiples_up_to") is None or q <= e["multiples_up_to"])
    return F


def fn_unit_dimension_allowed(ctx):
    dim, sd = _get(ctx, "net_quantity.dimension")
    tags, st = _tags(ctx)
    if sd == U: return U
    entries = _dated(ctx.tables["fourth_schedule_unit_exceptions"]["entries"], ctx.on_date)
    hits = [e for e in entries if e["tag"] in tags]
    if hits:
        declared = {dim}
        if ctx.facts.get("net_quantity.mass_equivalent").present: declared.add("mass")
        ok = any(set(combo) <= declared for e in hits for combo in e["allowed"])
        ctx.notes.append(f"Fourth Schedule entry {hits[0]['sl']} allows {hits[0]['allowed']}")
        return tv(ok)
    if st == U: return U
    state, ss = _get(ctx, "product.physical_state")
    if ss == U: return U
    expected = ctx.tables["rule12_default_dimension_by_state"].get(state)
    if expected is None: return U
    ctx.notes.append(f"Rule 12(2): {state} -> {expected}")
    return tv(dim == expected)


def fn_no_misleading_quantity_terms(ctx, table_version):
    text, s = _get(ctx, "net_quantity.text")
    if s == U: return U
    ver = next(v for v in ctx.tables["rule12_6_misleading_quantity_terms"]["versions"] if v["effective_from"] == table_version)
    low = str(text).lower()
    found = [t for t in ver["terms"] if (t == "*" and "*" in low) or (t != "*" and re.search(r"(?<![a-z])" + re.escape(t) + r"(?![a-z])", low))]
    if found:
        ctx.notes.append(f"misleading term(s): {found}")
        return F
    if ver["mode"] == "any_word_whatsoever":
        allowed = r"net|wt|weight|quantity|qty|contents?|vol|volume|mass|e|℮|n|u|g|gm|gms|kg|mg|ml|l|ltr|litre|liter|cm|m|mm|pieces?|pcs|units?|nos?|number|dm2|m2|cm2"
        leftover = [w for w in re.findall(r"[a-z℮]+", low) if not re.fullmatch(allowed, w)]
        if leftover:
            ctx.notes.append(f"unrecognised word(s) next to quantity: {leftover}")
            return U
    return T


def fn_unit_convention_ok(ctx):
    dim, s1 = _get(ctx, "net_quantity.dimension")
    base, s2 = _get(ctx, "net_quantity.base_value")
    unit, s3 = _get(ctx, "net_quantity.canonical_unit")
    if U in (s1, s2, s3): return U
    conv = ctx.tables["rule13_unit_conventions"].get(dim)
    if not conv: return U
    th = conv["threshold_base"]
    if math.isclose(base, th): return tv(unit in (conv["at_or_above_unit"], conv["exactly_threshold_may_use"]))
    expected = conv["below_threshold_unit"] if base < th else conv["at_or_above_unit"]
    if unit != expected: ctx.notes.append(f"expected unit '{expected}' for {base:g} base units, found '{unit}'")
    return tv(unit == expected)


def fn_si_units_only(ctx):
    text, s = _get(ctx, "net_quantity.text")
    if s == U: return U
    low = str(text).lower()
    bad = [t for t in ctx.tables["units"]["banned_non_si_terms"] if re.search(r"(?<![a-z])" + re.escape(t) + r"(?![a-z])", low)]
    if bad: ctx.notes.append(f"non-SI unit(s): {bad}")
    return tv(not bad)


def fn_mrp_format_ok(ctx, returnable=False):
    text, s = _get(ctx, "mrp.text")
    if s == U: return U
    t = ctx.tables["mrp_format"]
    pats = [t["returnable_bottle_pattern"]] if returnable else t["patterns_2011"]
    return tv(any(re.search(p, str(text)) for p in pats))


def fn_mrp_rounding_ok(ctx):
    v, s = _get(ctx, "mrp.value")
    if s == U: return U
    paise = int(round(float(v) * 100)) % 100
    return tv(paise in ctx.tables["mrp_format"]["rounding_allowed_paise_2011"])


def fn_has_sticker_type(ctx, type):
    st = ctx.facts.get("label.stickers")
    return tv(st.present and any(x.get("type") == type for x in st.value))


def fn_mrp_reduction_stickers_ok(ctx):
    stickers, s1 = _get(ctx, "label.stickers")
    mrp, s2 = _get(ctx, "mrp.value")
    if U in (s1, s2): return U
    res = []
    for x in stickers:
        if x.get("type") != "mrp_reduction": continue
        if x.get("revised_mrp") is None or x.get("covers_original_mrp") is None:
            res.append(U); continue
        res.append(tv(float(x["revised_mrp"]) < float(mrp) and not x["covers_original_mrp"]))
    return k_and(res)


def fn_selling_price_within_mrp(ctx):
    sp, s1 = _get(ctx, "transaction.selling_price")
    mrp, s2 = _get(ctx, "mrp.value")
    if U in (s1, s2): return U
    return tv(float(sp) <= float(mrp))


def fn_has_any_tag_from_table(ctx, table):
    tags, st = _tags(ctx)
    if st == U: return U
    return tv(any(t in ctx.tables[table]["tags"] for t in tags))


def fn_container_declaration_ok(ctx):
    tags, st = _tags(ctx)
    if st == U: return U
    need = ["containers.count"]
    if "container_bag" in tags: need += ["containers.length"]
    if "container_rectangular" in tags: need += ["containers.length", "containers.width"]
    if "container_round" in tags: need += ["containers.diameter"]
    return k_and(_get(ctx, p)[1] if ctx.facts.get(p).present else missing_result(p, "exists", ctx) for p in need)


def _band(bands, x):
    for b in bands:
        if x > b["above"] and (b["up_to"] is None or x <= b["up_to"]):
            return b
    return bands[0] if x <= bands[0]["up_to"] else None


def fn_numeral_height_ok(ctx, table):
    h, s1 = _get(ctx, "label.numeral_height_mm")
    key_path = "net_quantity.base_value" if "table1" in table else "label.pdp_area_cm2"
    key, s2 = _get(ctx, key_path)
    if U in (s1, s2): return U
    emb = ctx.facts.get("label.is_embossed")
    b = _band(ctx.tables[table]["bands"], float(key))
    need = b["embossed_mm"] if (emb.present and emb.value) else b["normal_mm"]
    ctx.notes.append(f"minimum numeral height {need} mm; measured {h} mm")
    return tv(float(h) >= need)


def fn_letter_size_ok(ctx):
    h, s1 = _get(ctx, "label.min_letter_height_mm")
    r, s2 = _get(ctx, "label.min_letter_width_ratio")
    if U in (s1, s2): return U
    t = ctx.tables["rule7_letter_size"]
    emb = ctx.facts.get("label.is_embossed")
    need = t["min_letter_height_mm"]["embossed" if (emb.present and emb.value) else "normal"]
    return tv(float(h) >= need and float(r) >= t["min_width_to_height_ratio"])


def fn_quantity_clear_space_ok(ctx):
    c, s = _get(ctx, "net_quantity.clearance")
    if s == U: return U
    try:
        nh = float(c["numeral_height"])
        t = ctx.tables["rule8_quantity_clear_space"]
        v_ok = min(float(c["above"]), float(c["below"])) >= t["min_vertical_clearance_x_numeral_height"] * nh
        h_ok = min(float(c["left"]), float(c["right"])) >= t["min_horizontal_clearance_x_numeral_height"] * nh
    except (KeyError, TypeError, ValueError):
        return U
    return tv(v_ok and h_ok)


def mpe(declared: float, dimension: str, tables) -> float:
    if dimension in ("mass", "volume"):
        t = tables["first_schedule_mpe_weight_volume"]
        b = _band(t["bands"], declared)
        if "absolute" in b:
            return float(b["absolute"])
        raw = declared * b["percent"] / 100
        return round(raw, 1) if declared <= 1000 else float(math.ceil(raw - 1e-9))
    t = tables["first_schedule_mpe_length_area_number"]
    if dimension == "length":
        pct = t["length"]["percent_up_to_threshold"] if declared <= t["length"]["threshold_cm"] else t["length"]["percent_above_threshold"]
    elif dimension == "area":
        pct = t["area"]["percent_up_to_threshold"] if declared <= t["area"]["threshold_cm2"] else t["area"]["percent_above_threshold"]
    else:
        pct = t["number"]["percent"]
    return declared * pct / 100


def fn_single_package_within_mpe(ctx):
    decl, s1 = _get(ctx, "net_quantity.base_value")
    dim, s2 = _get(ctx, "net_quantity.dimension")
    act, s3 = _get(ctx, "measurement.actual_net_quantity_base")
    if U in (s1, s2, s3): return U
    limit = mpe(decl, dim, ctx.tables)
    short = decl - float(act)
    ctx.notes.append(f"declared {decl:g}, measured {act}, shortage {short:g}, MPE {limit:g}")
    if short <= limit + 1e-9: return T
    text = ctx.facts.get("net_quantity.text")
    if text.present and re.search(r"(?i)when\s+packed", str(text.value)):
        ctx.notes.append("'when packed' — 21(3) proviso: officer to assess environmental loss")
        return U
    return F


def fn_lot_test_ok(ctx):
    decl, s1 = _get(ctx, "net_quantity.base_value")
    dim, s2 = _get(ctx, "net_quantity.dimension")
    samples, s3 = _get(ctx, "measurement.sample_net_quantities_base")
    lot, s4 = _get(ctx, "measurement.lot_size")
    if U in (s1, s2, s3, s4): return U
    need = 32 if lot < 4000 else 80
    if lot == 4000: ctx.notes.append("lot size exactly 4000 not covered by Fifth Schedule; used 80")
    limit = mpe(decl, dim, ctx.tables)
    avg = sum(samples) / len(samples)
    worst = decl - min(samples)
    ctx.notes.append(f"n={len(samples)} (required {need}), avg {avg:.2f} vs declared {decl:g}, worst shortage {worst:.2f} vs MPE {limit:g}")
    return tv(len(samples) >= need and avg >= decl and worst <= limit + 1e-9)


def fn_ad_font_sizes_match(ctx):
    a, s1 = _get(ctx, "ad.net_quantity_font_px")
    b, s2 = _get(ctx, "ad.rsp_font_px")
    if U in (s1, s2): return U
    return tv(abs(float(a) - float(b)) / float(b) <= 0.10)   # 10% measurement tolerance: ENGINEERING_POLICY


def fn_draft_unknown(ctx, **_):
    ctx.notes.append("draft operator — not implemented until amended text is verified")
    return U


FUNCTIONS = {
    "is_second_schedule_commodity": fn_is_second_schedule_commodity,
    "standard_pack_size_ok": fn_standard_pack_size_ok,
    "unit_dimension_allowed": fn_unit_dimension_allowed,
    "no_misleading_quantity_terms": fn_no_misleading_quantity_terms,
    "unit_convention_ok": fn_unit_convention_ok,
    "si_units_only": fn_si_units_only,
    "mrp_format_ok": fn_mrp_format_ok,
    "mrp_rounding_ok": fn_mrp_rounding_ok,
    "has_sticker_type": fn_has_sticker_type,
    "mrp_reduction_stickers_ok": fn_mrp_reduction_stickers_ok,
    "selling_price_within_mrp": fn_selling_price_within_mrp,
    "has_any_tag_from_table": fn_has_any_tag_from_table,
    "container_declaration_ok": fn_container_declaration_ok,
    "numeral_height_ok": fn_numeral_height_ok,
    "letter_size_ok": fn_letter_size_ok,
    "quantity_clear_space_ok": fn_quantity_clear_space_ok,
    "single_package_within_mpe": fn_single_package_within_mpe,
    "lot_test_ok": fn_lot_test_ok,
    "ad_font_sizes_match": fn_ad_font_sizes_match,
    "usp_equals_rsp": fn_draft_unknown,
    "unit_sale_price_ok": fn_draft_unknown,
}


# --------------------------------------------------------------------------- rule evaluation
def select_rules(ruleset, on_date: date, include_drafts=False):
    out = []
    for r in ruleset["rules"]:
        if r["status"] != "active" and not (include_drafts and r["status"] == "draft"):
            continue
        lo = date.fromisoformat(r["effective_from"])
        hi = date.fromisoformat(r["effective_to"]) if r["effective_to"] else date.max
        if lo <= on_date <= hi:
            out.append(r)
    return out


def evaluate_rule(rule, facts, ruleset, tables, on_date):
    def new_ctx(phase):
        return Ctx(facts, ruleset, tables, on_date, phase=phase, mode=rule["verification_mode"])

    base = {
        "rule_id": rule["rule_id"], "version": rule["version"], "title": rule["title"],
        "provision": rule["provision"]["rule"], "severity": rule["severity"],
        "verification_mode": rule["verification_mode"], "threshold_source": rule["threshold_source"],
    }

    a = new_ctx("applicability")
    applies = evaluate(rule["applies_when"], a)
    if applies == F:
        return {**base, "status": "NOT_APPLICABLE", "assumptions": a.assumptions}

    # exemptions are checked even when applicability is UNKNOWN: a certain exemption settles the rule
    unknown_exemptions = []
    for ex in rule["exempt_when"]:
        e = new_ctx("exemption")
        r = evaluate(ex["when"], e)
        if r == T:
            return {**base, "status": "EXEMPT", "exemption_ref": ex["exemption_ref"], "reason": ex["reason"], "assumptions": a.assumptions + e.assumptions}
        if r == U:
            unknown_exemptions.append({"ref": ex["exemption_ref"], "missing_facts": sorted(e.missing | e.low_conf)})

    if applies == U:
        return {**base, "status": "REQUIRES_VERIFICATION", "queue": "REVIEW",
                "reason": "Could not determine whether this rule applies",
                "missing_facts": sorted(a.missing), "low_confidence_facts": sorted(a.low_conf), "assumptions": a.assumptions}

    c = new_ctx("check")
    result = evaluate(rule["check"], c)
    evidence = [{"fact": p, "value": f_.value, "confidence": f_.confidence, "source": f_.source, "evidence": f_.evidence}
                for p, f_ in c.used.items()]
    out = {**base, "evidence": evidence, "assumptions": a.assumptions + c.assumptions, "notes": c.notes}
    manual = rule["verification_mode"] not in AUTOMATED_MODES

    if result == T:
        return {**out, "status": "COMPLIANT"}
    if result == F:
        if unknown_exemptions:
            return {**out, "status": "REQUIRES_VERIFICATION", "queue": "REVIEW",
                    "reason": "Check failed but an exemption could not be ruled out", "possible_exemptions": unknown_exemptions}
        status = rule["outcome_on_fail"]
        o = {**out, "status": status, "reason": rule["fail_message"], "missing_facts": sorted(c.missing)}
        if status == "REQUIRES_VERIFICATION": o["queue"] = "REVIEW"
        return o
    return {**out, "status": "REQUIRES_VERIFICATION",
            "queue": "MANUAL_CHECKLIST" if manual else "REVIEW",
            "reason": ("Needs officer input / measurement / lookup" if manual else "Could not be decided from extracted data"),
            "missing_facts": sorted(c.missing), "low_confidence_facts": sorted(c.low_conf)}


def run(facts_raw: dict, on_date: date | None = None, include_drafts=False, ruleset=None, tables=None):
    ruleset = ruleset or load_ruleset()
    tables = tables or load_tables()
    if on_date is None:
        d = facts_raw.get("inspection.date")
        d = d["value"] if isinstance(d, dict) else d
        on_date = date.fromisoformat(d) if d else date.today()
    facts = FactStore(facts_raw, tables)
    rules = select_rules(ruleset, on_date, include_drafts)
    results = [evaluate_rule(r, facts, ruleset, tables, on_date) for r in rules]

    count = lambda s, q=None: sum(1 for r in results if r["status"] == s and (q is None or r.get("queue") == q))
    if count("NON_COMPLIANT"):
        verdict = "NON_COMPLIANT"
    elif count("REQUIRES_VERIFICATION", "REVIEW"):
        verdict = "REQUIRES_VERIFICATION"
    elif count("EXEMPT") and not count("COMPLIANT") and not count("REQUIRES_VERIFICATION"):
        verdict = "EXEMPT"
    else:
        verdict = "COMPLIANT"
    return {
        "rule_set_id": ruleset["rule_set_id"], "rule_set_version": ruleset["rule_set_version"],
        "judged_as_of": on_date.isoformat(), "rules_evaluated": len(rules),
        "automated_verdict": verdict,
        "counts": {s: count(s) for s in ["NON_COMPLIANT", "REQUIRES_VERIFICATION", "COMPLIANT", "EXEMPT", "NOT_APPLICABLE", "OBSERVATION"]},
        "open_manual_checklist": count("REQUIRES_VERIFICATION", "MANUAL_CHECKLIST"),
        "results": results,
    }


SEV = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3, "INFO": 4}
ICON = {"NON_COMPLIANT": "FAIL", "REQUIRES_VERIFICATION": "VERIFY", "COMPLIANT": "PASS", "EXEMPT": "EXEMPT", "OBSERVATION": "NOTE", "NOT_APPLICABLE": "n/a"}


def print_report(rep, name):
    print(f"\n=== {name} | judged as of {rep['judged_as_of']} | {rep['rules_evaluated']} rules in force ===")
    print(f"AUTOMATED VERDICT: {rep['automated_verdict']}   counts={rep['counts']}   open manual checklist={rep['open_manual_checklist']}")
    order = ["NON_COMPLIANT", "REQUIRES_VERIFICATION", "OBSERVATION", "COMPLIANT"]
    for st in order:
        rows = sorted([r for r in rep["results"] if r["status"] == st and r.get("queue") != "MANUAL_CHECKLIST"], key=lambda r: SEV[r["severity"]])
        for r in rows:
            extra = r.get("reason") or r.get("exemption_ref") or ""
            if r.get("missing_facts") or r.get("low_confidence_facts"):
                extra += f"  [missing={r.get('missing_facts')}, low_conf={r.get('low_confidence_facts')}]"
            if r.get("possible_exemptions"):
                extra += f"  [possible exemptions: {[e['ref'] for e in r['possible_exemptions']]}]"
            if r.get("notes"):
                extra += f"  notes={r['notes']}"
            print(f"  {ICON[st]:7} {r['severity']:8} {r['rule_id']:18} R.{r['provision']:28} {r['title'][:60]}")
            if st != "COMPLIANT" and extra:
                print(f"          -> {extra}")
    groups = {}
    for r in rep["results"]:
        if r["status"] == "EXEMPT":
            groups.setdefault(r["exemption_ref"], []).append(r["rule_id"])
    for ref, ids in groups.items():
        print(f"  EXEMPT  under {ref}: {', '.join(ids)}")
    manual = [r["rule_id"] for r in rep["results"] if r.get("queue") == "MANUAL_CHECKLIST"]
    if manual:
        print(f"  manual checklist: {', '.join(manual)}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("facts")
    ap.add_argument("--date", help="judge under the rules in force on this date (YYYY-MM-DD)")
    ap.add_argument("--include-drafts", action="store_true")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    raw = json.loads(Path(a.facts).read_text())
    rep = run(raw, date.fromisoformat(a.date) if a.date else None, a.include_drafts)
    if a.json:
        json.dump(rep, sys.stdout, indent=2, ensure_ascii=False, default=str)
    else:
        print_report(rep, Path(a.facts).stem)
