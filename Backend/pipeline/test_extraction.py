"""Tests for the parts of extraction that must not depend on a model.

Run from the Backend directory:  python -m pipeline.test_extraction   (or python -m pytest -q)

The model is free to miss a field; these guard what happens next - the label is read by pattern,
nothing is invented, and the facts derived from a declaration say what the label actually says.
"""
from pipeline.extraction.declarations import PackageDeclarations, Declared
from pipeline.extraction import patterns
from pipeline.normalization import declarations as normalization


def declared(value):
    return Declared(value=value, confidence=1.0)


def scanned(ocr):
    return {field: item.value for field, item in patterns.scan(ocr).items()}


def test_quantity_price_and_date_are_read_off_the_label():
    found = scanned("Net Wt. 70 g\nM.R.P. Rs. 14.00\n(Incl. of all taxes)\nMFD: 08/2025")
    assert found["net_quantity_value"] == "70"
    assert found["net_quantity_unit"] == "g"
    assert found["mrp_value"] == "14.00"
    assert found["manufacturing_month"] == "8" and found["manufacturing_year"] == "2025"


def test_a_declaration_split_across_two_lines_is_read_as_one():
    found = scanned("NET WEIGHT\n1.5 KG\nMAXIMUM RETAIL PRICE\nRs.255/- (inclusive of all taxes)")
    assert found["net_quantity_value"] == "1.5" and found["net_quantity_unit"] == "KG"
    assert found["mrp_value"] == "255"
    assert "inclusive of all taxes" in found["mrp_text"].lower()


def test_dates_in_several_forms():
    assert scanned("Packed on: AUG 2025")["manufacturing_month"] == "8"
    assert scanned("Mfg: 07/25")["manufacturing_year"] == "2025"
    assert scanned("DATE OF MANUFACTURE\n15.08.2025")["manufacturing_month"] == "8"
    assert scanned("Lot 5/2025 MFD 08/2025")["manufacturing_month"] == "8"


def test_a_shelf_life_date_is_never_a_date_of_manufacture():
    assert "manufacturing_month" not in scanned("Best Before 06/2026\nUse by 12/2026")


def test_a_party_declaration_does_not_make_the_address_below_it_a_date():
    assert "manufacturing_month" not in scanned("Packed by: ACME\nPlot 12-25, Phase 2, Pune")
    assert scanned("Mfd. by: ACME\nPlot 12-25, Pune\nMFD: 08/2025")["manufacturing_month"] == "8"


def test_an_address_is_not_read_as_a_quantity():
    assert "net_quantity_value" not in scanned("Nestle India Ltd, 100 Gurgaon Road\nTel: 1800 103 1947")


def test_nothing_is_filled_when_the_label_carries_nothing():
    empty = PackageDeclarations(product_name=declared("Tasty Namkeen"))
    result, filled = patterns.backfill("Tasty Namkeen\nA product of India", empty)
    assert filled == []
    assert result.net_quantity_value.value is None and result.mrp_value.value is None


def test_backfill_fills_the_numbers_the_model_left_empty():
    # what the model returns often: the wording, none of the numbers
    extracted = PackageDeclarations(mrp_text=declared("M.R.P. Rs. 14.00"), net_quantity_text=declared("Net Wt. 70 g"))
    result, filled = patterns.backfill("Net Wt. 70 g\nM.R.P. Rs. 14.00\n(Incl. of all taxes)\nMFD: 08/2025", extracted)
    assert result.net_quantity_value.value == "70" and result.net_quantity_unit.value == "g"
    assert result.mrp_value.value == "14.00"
    assert result.manufacturing_month.value == "8" and result.manufacturing_year.value == "2025"
    assert filled


def test_backfill_never_overwrites_what_the_model_read():
    extracted = PackageDeclarations(net_quantity_text=declared("Net Wt. 70 g"), net_quantity_value=declared("70"))
    result, _ = patterns.backfill("Net Wt. 999 kg", extracted)
    assert result.net_quantity_value.value == "70"


def test_backfill_completes_a_declaration_the_model_read_only_half_of():
    extracted = PackageDeclarations(mrp_text=declared("M.R.P. Rs. 14.00"))
    result, _ = patterns.backfill("M.R.P. Rs. 14.00\n(Incl. of all taxes)", extracted)
    assert result.mrp_text.value == "M.R.P. Rs. 14.00 (Incl. of all taxes)"


def test_country_of_origin_india_does_not_make_a_package_imported():
    for origin in ("India", "INDIA", "Made in India", "Bharat"):
        facts = normalization.build_facts({"product.country_of_manufacture": {"value": origin, "confidence": 1.0}}, 1, "t")
        assert facts["product.is_imported"] is False, origin
        assert facts["product.country_of_manufacture"]["value"] == "India", origin


def test_a_foreign_origin_or_a_named_importer_makes_a_package_imported():
    foreign = normalization.build_facts({"product.country_of_manufacture": {"value": "China", "confidence": 1.0}}, 1, "t")
    assert foreign["product.is_imported"] is True
    imported = normalization.build_facts({"importer.name": {"value": "ACME IMPORTS", "confidence": 1.0}}, 1, "t")
    assert imported["product.is_imported"] is True


def facts_from(**values):
    return normalization.build_facts(
        {path.replace("__", "."): {"value": value, "confidence": 1.0} for path, value in values.items()}, 1, "t"
    )


def test_a_phone_keeps_only_the_number_so_the_rule_can_match_it():
    import re
    rule = re.compile(r"^[+0-9()\-\s]{8,20}$")
    for printed in ("Tel: 1800 103 1947", "Ph. +91-22-1234-5678", "Customer Care No.: 1800-123-4567 (toll free)"):
        assert rule.match(facts_from(consumer_care__phone=printed)["consumer_care.phone"]["value"]), printed
    # nothing to find means nothing is changed, and the rule still fails
    assert facts_from(consumer_care__phone="Contact us")["consumer_care.phone"]["value"] == "Contact us"


def test_an_email_keeps_only_the_address():
    assert facts_from(consumer_care__email="Email: care@in.nestle.com")["consumer_care.email"]["value"] == "care@in.nestle.com"


def test_the_pin_code_is_derived_from_the_address():
    facts = facts_from(manufacturer__address__text="Plot No. 1, IMT Manesar, Gurugram, Haryana - 122050")
    assert facts["manufacturer.address.pin"]["value"] == "122050"
    assert "manufacturer.address.pin" not in facts_from(manufacturer__address__text="Industrial Estate")


if __name__ == "__main__":
    import inspect, sys
    fails = 0
    for name, fn in list(globals().items()):
        if name.startswith("test_") and inspect.isfunction(fn):
            try:
                fn(); print("ok  ", name)
            except AssertionError as e:
                fails += 1; print("FAIL", name, e)
    sys.exit(1 if fails else 0)
