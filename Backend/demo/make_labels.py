from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

OUT = Path(__file__).resolve().parent / "labels"
FONT_DIR = Path("C:/Windows/Fonts")
W, H = 1000, 1400


def font(size: int, bold: bool = False):
    name = "arialbd.ttf" if bold else "arial.ttf"
    path = FONT_DIR / name
    if path.exists():
        return ImageFont.truetype(str(path), size)
    return ImageFont.load_default(size)


def panel(bg: str):
    image = Image.new("RGB", (W, H), bg)
    return image, ImageDraw.Draw(image)


def block(draw, x, y, lines, size=34, bold=False, fill="black", spacing=14):
    f = font(size, bold)
    for line in lines:
        draw.text((x, y), line, font=f, fill=fill)
        y += size + spacing
    return y


def rule(draw, y, color="#8a8a8a"):
    draw.line([(60, y), (W - 60, y)], fill=color, width=3)
    return y + 30


def biscuit_front():
    image, draw = panel("#f6efdc")
    draw.rectangle([40, 40, W - 40, H - 40], outline="#7a5c2e", width=6)
    y = block(draw, 80, 120, ["SUNRISE"], size=96, bold=True, fill="#7a5c2e")
    y = block(draw, 80, y + 10, ["Glucose Biscuits"], size=64, bold=True, fill="#3a2c14")
    y = rule(draw, y + 30)
    y = block(draw, 80, y, ["Crisp baked wheat biscuits", "with milk and glucose"], size=36, fill="#4a3a1c")
    y = rule(draw, y + 40)
    y = block(draw, 80, y, ["Net Wt. 200 g"], size=62, bold=True)
    y = block(draw, 80, y + 20, ["MRP Rs. 45.00", "(inclusive of all taxes)"], size=48, bold=True)
    block(draw, 80, H - 200, ["Mfd. 06/2026", "Best before 9 months from packing"], size=34, fill="#4a3a1c")
    return image


def biscuit_back():
    image, draw = panel("#fbf7ec")
    draw.rectangle([40, 40, W - 40, H - 40], outline="#7a5c2e", width=4)
    y = block(draw, 80, 110, ["Manufactured by"], size=40, bold=True)
    y = block(draw, 80, y + 6, [
        "Sunrise Foods Pvt Ltd",
        "Plot 14, MIDC Industrial Area",
        "Pune, Maharashtra 411019",
        "India",
    ], size=36)
    y = rule(draw, y + 20)
    y = block(draw, 80, y, ["Net Wt. 200 g", "MRP Rs. 45.00 (inclusive of all taxes)"], size=40, bold=True)
    y = block(draw, 80, y + 10, ["Month and year of manufacture: 06/2026"], size=34)
    y = rule(draw, y + 20)
    y = block(draw, 80, y, ["Consumer complaints contact"], size=40, bold=True)
    y = block(draw, 80, y + 6, [
        "Consumer Care Manager",
        "Sunrise Foods Pvt Ltd",
        "Plot 14, MIDC Industrial Area",
        "Pune, Maharashtra 411019",
        "Phone: 020-24567890",
        "Email: care@sunrisefoods.co.in",
    ], size=34)
    block(draw, 80, H - 150, ["Ingredients: Wheat flour, sugar, edible oil,", "glucose, salt, raising agents"], size=30)
    return image


def shampoo_front():
    image, draw = panel("#e8f2f7")
    draw.rectangle([40, 40, W - 40, H - 40], outline="#1d5f7a", width=6)
    y = block(draw, 80, 130, ["AQUAPURE"], size=92, bold=True, fill="#1d5f7a")
    y = block(draw, 80, y + 10, ["Anti-Dandruff Shampoo"], size=58, bold=True, fill="#123c4e")
    y = rule(draw, y + 30, "#6fa3b8")
    y = block(draw, 80, y, ["For dry and flaky scalp", "With tea tree and neem"], size=36, fill="#20506a")
    y = rule(draw, y + 40, "#6fa3b8")
    y = block(draw, 80, y, ["Net Vol. about 100 ml"], size=60, bold=True)
    block(draw, 80, H - 220, ["Gentle daily care", "Dermatologically tested"], size=34, fill="#20506a")
    return image


def shampoo_back():
    image, draw = panel("#f2f9fc")
    draw.rectangle([40, 40, W - 40, H - 40], outline="#1d5f7a", width=4)
    y = block(draw, 80, 110, ["Manufactured by"], size=40, bold=True)
    y = block(draw, 80, y + 6, [
        "Aquapure Personal Care Ltd",
        "Survey 88, Baddi Industrial Area",
        "Solan, Himachal Pradesh 173205",
        "India",
    ], size=36)
    y = rule(draw, y + 20, "#6fa3b8")
    y = block(draw, 80, y, ["Net Vol. about 100 ml"], size=42, bold=True)
    y = block(draw, 80, y + 10, ["Month and year of manufacture: 04/2026"], size=34)
    y = rule(draw, y + 20, "#6fa3b8")
    y = block(draw, 80, y, ["Consumer complaints contact"], size=40, bold=True)
    y = block(draw, 80, y + 6, [
        "Customer Relations Officer",
        "Aquapure Personal Care Ltd",
        "Survey 88, Baddi Industrial Area",
        "Solan, Himachal Pradesh 173205",
        "Phone: 1800-123-4567",
    ], size=34)
    block(draw, 80, H - 170, ["Directions: Apply to wet hair, lather,", "rinse thoroughly. Avoid contact with eyes."], size=30)
    return image


PANELS = {
    "biscuit_front.png": biscuit_front,
    "biscuit_back.png": biscuit_back,
    "shampoo_front.png": shampoo_front,
    "shampoo_back.png": shampoo_back,
}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for name, builder in PANELS.items():
        builder().save(OUT / name)
        print("wrote", OUT / name)
    print()
    print("biscuit_*  : complete declarations, expected to pass the label checks")
    print("shampoo_*  : MRP omitted and quantity written 'about 100 ml' (Rule 12(6))")


if __name__ == "__main__":
    main()
