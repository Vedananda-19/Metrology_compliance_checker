import cv2
import numpy as np
import re

MRP_PATTERN = re.compile(r"m\.?r\.?p|maximum\s+retail|retail\s+sale\s+price|\brs\.?\b|₹", re.IGNORECASE)
QUANTITY_PATTERN = re.compile(r"net\s*(?:wt|weight|vol|volume|qty|quantity)|\b\d+(?:\.\d+)?\s*(?:g|gm|kg|ml|l|cm|m)\b", re.IGNORECASE)


def relative_luminance(bgr):
    channels = np.array(bgr, dtype=np.float64) / 255.0
    channels = np.where(channels <= 0.03928, channels / 12.92, ((channels + 0.055) / 1.055) ** 2.4)
    blue, green, red = channels
    return 0.2126 * red + 0.7152 * green + 0.0722 * blue


def contrast_ratio(image, region, pad: int = 6):
    height, width = image.shape[:2]
    x1 = max(region["x1"] - pad, 0)
    y1 = max(region["y1"] - pad, 0)
    x2 = min(region["x2"] + pad, width)
    y2 = min(region["y2"] + pad, height)
    if x2 - x1 < 4 or y2 - y1 < 4:
        return None

    crop = image[y1:y2, x1:x2]
    gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
    _, mask = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    ink = mask == 0
    paper = mask == 255
    if ink.sum() < 12 or paper.sum() < 12:
        return None

    ink_colour = crop[ink].mean(axis=0)
    paper_colour = crop[paper].mean(axis=0)
    lighter = max(relative_luminance(ink_colour), relative_luminance(paper_colour))
    darker = min(relative_luminance(ink_colour), relative_luminance(paper_colour))
    return round((lighter + 0.05) / (darker + 0.05), 2)


def text_height_px(region):
    polygon = region.get("polygon") or []
    if len(polygon) == 4:
        left = abs(polygon[3][1] - polygon[0][1])
        right = abs(polygon[2][1] - polygon[1][1])
        return max(left, right)
    return region["y2"] - region["y1"]


def clearance_px(region, neighbours, image_width, image_height):
    above = region["y1"]
    below = image_height - region["y2"]
    left = region["x1"]
    right = image_width - region["x2"]

    for other in neighbours:
        if other is region:
            continue
        horizontal_overlap = other["x1"] < region["x2"] and other["x2"] > region["x1"]
        vertical_overlap = other["y1"] < region["y2"] and other["y2"] > region["y1"]
        if horizontal_overlap:
            if other["y2"] <= region["y1"]:
                above = min(above, region["y1"] - other["y2"])
            elif other["y1"] >= region["y2"]:
                below = min(below, other["y1"] - region["y2"])
        if vertical_overlap:
            if other["x2"] <= region["x1"]:
                left = min(left, region["x1"] - other["x2"])
            elif other["x1"] >= region["x2"]:
                right = min(right, other["x1"] - region["x2"])

    return {
        "above": int(above),
        "below": int(below),
        "left": int(left),
        "right": int(right),
        "numeral_height": int(text_height_px(region)),
    }


def principal_panel(regions, width, height):
    if not regions:
        return None
    x1 = min(r["x1"] for r in regions)
    y1 = min(r["y1"] for r in regions)
    x2 = max(r["x2"] for r in regions)
    y2 = max(r["y2"] for r in regions)
    area_px = max((x2 - x1) * (y2 - y1), 1)
    return {
        "bbox": [x1, y1, x2, y2],
        "coverage": round(area_px / float(width * height), 3),
    }


def analyse(panels):
    facts = {}
    signals = {"panels": []}

    mrp_region = None
    mrp_image = None
    quantity_region = None
    quantity_image = None
    quantity_panel = None

    for panel in panels:
        image = panel["image"]
        regions = panel["regions"]
        height, width = image.shape[:2]
        summary = principal_panel(regions, width, height)
        signals["panels"].append(
            {
                "image_id": panel["image_id"],
                "width": width,
                "height": height,
                "region_count": len(regions),
                "principal_panel": summary,
            }
        )
        for region in regions:
            if mrp_region is None and MRP_PATTERN.search(region["text"]):
                mrp_region, mrp_image = region, image
            if quantity_region is None and QUANTITY_PATTERN.search(region["text"]):
                quantity_region, quantity_image, quantity_panel = region, image, panel

    if mrp_region is not None:
        ratio = contrast_ratio(mrp_image, mrp_region)
        if ratio is not None:
            facts["mrp.contrast_ratio"] = {"value": ratio, "confidence": 0.8, "extractor": "cv:contrast"}

    if quantity_region is not None:
        ratio = contrast_ratio(quantity_image, quantity_region)
        if ratio is not None:
            facts["net_quantity.contrast_ratio"] = {"value": ratio, "confidence": 0.8, "extractor": "cv:contrast"}
        height, width = quantity_image.shape[:2]
        facts["net_quantity.clearance"] = {
            "value": clearance_px(quantity_region, quantity_panel["regions"], width, height),
            "confidence": 0.75,
            "extractor": "cv:clearance",
        }
        signals["quantity_text_height_px"] = int(text_height_px(quantity_region))

    confidences = [r["confidence"] for panel in panels for r in panel["regions"]]
    if confidences:
        facts["label.min_declaration_ocr_confidence"] = {
            "value": round(min(confidences), 3),
            "confidence": 0.9,
            "extractor": "cv:ocr_quality",
        }

    return {"facts": facts, "signals": signals}
