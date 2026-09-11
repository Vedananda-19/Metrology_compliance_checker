from pydantic import BaseModel, Field
from pipeline import llm
import re

KEYWORD_TAGS = {
    "biscuits": ["biscuit", "cookie", "cracker"],
    "bread": ["bread", "bun", "pav"],
    "salt": ["salt", "iodised salt", "iodized salt"],
    "tea": ["tea", "chai"],
    "coffee": ["coffee"],
    "atta": ["atta", "wheat flour", "maida", "chakki"],
    "rice": ["rice", "basmati"],
    "pulses": ["dal", "pulses", "lentil", "chana", "moong", "toor"],
    "milk_powder": ["milk powder", "dairy whitener"],
    "ice_cream": ["ice cream", "frozen dessert"],
    "edible_oil": ["edible oil", "sunflower oil", "mustard oil", "groundnut oil", "refined oil", "ghee"],
    "soft_drink_non_alcoholic": ["soft drink", "carbonated", "aerated", "cola", "soda"],
    "packaged_water": ["packaged drinking water", "mineral water"],
    "baby_food": ["infant", "baby food", "cereal for babies"],
    "spices": ["masala", "spice", "turmeric", "chilli powder", "haldi", "jeera"],
    "soap": ["soap", "bathing bar"],
    "detergent": ["detergent", "washing powder", "dishwash"],
    "shampoo": ["shampoo"],
    "toothpaste": ["toothpaste", "tooth paste", "dental cream"],
    "cosmetic": ["cream", "lotion", "moisturiser", "moisturizer", "shampoo", "conditioner", "talc", "cosmetic"],
    "paint_base": ["paint", "enamel", "primer", "distemper"],
    "cement": ["cement"],
    "fertilizer": ["fertilizer", "fertiliser", "urea"],
    "towel": ["towel"],
    "bed_sheet": ["bed sheet", "bedsheet", "bed-sheet"],
    "saree": ["saree", "sari"],
    "dhoti": ["dhoti"],
    "napkin": ["napkin", "serviette"],
    "pillow_cover": ["pillow cover", "pillow case"],
    "table_cloth": ["table cloth", "tablecloth"],
    "toilet_paper": ["toilet paper", "toilet roll"],
    "facial_tissue": ["facial tissue", "tissue paper"],
    "aluminium_foil": ["aluminium foil", "aluminum foil"],
    "waxed_paper": ["waxed paper", "wax paper"],
}

FOOD_TAGS = {
    "biscuits", "bread", "salt", "tea", "coffee", "atta", "rice", "pulses", "milk_powder",
    "ice_cream", "edible_oil", "soft_drink_non_alcoholic", "packaged_water", "baby_food", "spices",
}
COSMETIC_TAGS = {"soap", "shampoo", "toothpaste", "cosmetic"}
TEXTILE_TAGS = {"towel", "bed_sheet", "saree", "dhoti", "napkin", "pillow_cover", "table_cloth"}
SHEET_TAGS = {"toilet_paper", "facial_tissue", "aluminium_foil", "waxed_paper"}

STATE_BY_TAG = {
    "edible_oil": "viscous",
    "shampoo": "liquid",
    "soft_drink_non_alcoholic": "liquid",
    "packaged_water": "liquid",
    "ice_cream": "liquid",
    "paint_base": "viscous",
    "towel": "countable",
    "bed_sheet": "countable",
    "saree": "countable",
    "napkin": "countable",
    "toilet_paper": "countable",
}

UNIT_STATE = {
    "g": "solid", "gm": "solid", "gms": "solid", "kg": "solid",
    "ml": "liquid", "l": "liquid", "ltr": "liquid", "litre": "liquid",
    "cm": "linear", "m": "linear", "mm": "linear",
    "n": "countable", "u": "countable", "pcs": "countable", "pieces": "countable",
}

CATEGORY_BY_GROUP = {
    "food": "Food and beverage",
    "cosmetic": "Cosmetic and personal care",
    "textile": "Textile",
    "sheet": "Sheet product",
    "household": "Household and other",
}


class ProductClassification(BaseModel):
    common_name: str | None = Field(default=None, description="Generic name of the commodity, not the brand")
    brand: str | None = Field(default=None, description="Brand name if printed")
    tags: list[str] = Field(default_factory=list, description="Commodity class tags from the allowed list only")
    physical_state: str | None = Field(
        default=None,
        description="One of solid, semi_solid, viscous, solid_liquid_mixture, liquid, cubic_measure, linear, area, countable",
    )
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    reasoning_summary: str | None = Field(default=None, description="One short sentence, no legal conclusions")


INGREDIENT_HEADING = re.compile(r"ingredient|contains|directions|nutrition|allerg|storage|caution", re.IGNORECASE)
COMPOUND_EXCEPTIONS = {"tea": ["tea tree"], "salt": ["salt free"], "cream": ["cream biscuit"]}


def name_scope(label_text: str, declarations: dict) -> str:
    parts = []
    for path in ("product.common_name", "product.name", "product.brand"):
        fact = declarations.get(path)
        if fact and fact.get("value"):
            parts.append(str(fact["value"]))

    for line in (label_text or "").splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if INGREDIENT_HEADING.search(stripped):
            break
        parts.append(stripped)
        if len(parts) > 8:
            break
    return " ".join(parts)


def keyword_tags(text: str):
    lowered = text.lower()
    found = []
    for tag, keywords in KEYWORD_TAGS.items():
        for keyword in keywords:
            if not re.search(r"(?<![a-z])" + re.escape(keyword), lowered):
                continue
            blocked = COMPOUND_EXCEPTIONS.get(tag, [])
            if blocked and all(
                re.search(r"(?<![a-z])" + re.escape(keyword) + r"(?![a-z])", lowered) is None
                or phrase in lowered
                for phrase in blocked
            ):
                continue
            found.append(tag)
            break
    return found


def expand_groups(tags):
    expanded = set(tags)
    if expanded & FOOD_TAGS:
        expanded.add("food")
    if expanded & COSMETIC_TAGS:
        expanded.add("cosmetic")
    if expanded & TEXTILE_TAGS:
        expanded.add("textile")
    if expanded & SHEET_TAGS:
        expanded.add("sheet_other")
    return sorted(expanded)


def category_for(tags):
    tagset = set(tags)
    if tagset & FOOD_TAGS or "food" in tagset:
        return CATEGORY_BY_GROUP["food"]
    if tagset & COSMETIC_TAGS or "cosmetic" in tagset:
        return CATEGORY_BY_GROUP["cosmetic"]
    if tagset & TEXTILE_TAGS:
        return CATEGORY_BY_GROUP["textile"]
    if tagset & SHEET_TAGS:
        return CATEGORY_BY_GROUP["sheet"]
    return CATEGORY_BY_GROUP["household"]


def state_for(tags, unit):
    for tag in tags:
        if tag in STATE_BY_TAG:
            return STATE_BY_TAG[tag]
    if unit:
        return UNIT_STATE.get(str(unit).strip().lower())
    return None


def classify_with_llm(text: str, allowed):
    messages = [
        (
            "system",
            "You classify a packaged commodity from the text printed on its label.\n"
            "Choose tags only from this list, and only those the text actually supports:\n"
            f"{', '.join(allowed)}\n"
            "Return an empty tag list and a low confidence when the text does not identify the commodity. "
            "Do not infer a category from the brand name alone. Do not mention legal rules or compliance.",
        ),
        ("human", f"Label text:\n\n{text}"),
    ]
    result = llm.invoke_structured(ProductClassification, messages)
    if result is None:
        return None
    result.tags = [t for t in result.tags if t in set(allowed)]
    return result


def run(label_text: str, declarations: dict, threshold: float = 0.6):
    deterministic = keyword_tags(name_scope(label_text, declarations))
    unit_fact = declarations.get("net_quantity.unit") or {}
    unit = unit_fact.get("value")

    tags = deterministic
    source = "keyword"
    confidence = 0.9 if deterministic else 0.2
    common_name = None
    brand = None
    state = None

    if llm.available():
        result = classify_with_llm(label_text, sorted(KEYWORD_TAGS.keys()))
        if result is not None:
            source = "llm"
            common_name = result.common_name
            brand = result.brand
            state = result.physical_state
            confidence = result.confidence
            merged = sorted(set(result.tags) | set(deterministic))
            if merged:
                tags = merged
                if deterministic and set(deterministic) & set(result.tags):
                    confidence = max(confidence, 0.85)

    if not common_name:
        fact = declarations.get("product.common_name") or {}
        common_name = fact.get("value")
    if not state:
        state = state_for(tags, unit)

    tags = expand_groups(tags)
    if not tags:
        confidence = min(confidence, 0.3)

    return {
        "common_name": common_name,
        "brand": brand,
        "tags": tags,
        "category": category_for(tags),
        "physical_state": state,
        "confidence": round(float(confidence), 3),
        "source": source,
        "needs_review": confidence < threshold or not tags,
    }
