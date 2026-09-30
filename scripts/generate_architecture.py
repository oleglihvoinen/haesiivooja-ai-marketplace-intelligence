from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

W, H = 1600, 900
BG = "#F7F9FC"
TEXT = "#152238"
MUTED = "#5C667A"
BORDER = "#D9E1EC"

OUT = Path(__file__).resolve().parents[1] / "docs" / "architecture.png"
OUT.parent.mkdir(parents=True, exist_ok=True)

def font(size, bold=False):
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/dejavu/DejaVuSans.ttf",
    ]
    for p in candidates:
        try:
            return ImageFont.truetype(p, size)
        except OSError:
            pass
    return ImageFont.load_default()

img = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(img)

title_f = font(38, True)
sub_f = font(20)
head_f = font(20, True)
body_f = font(17)
small_f = font(16)

d.text((70, 54), "HaeSiivooja AI Marketplace Intelligence Platform", fill=TEXT, font=title_f)
d.text((70, 104), "Web/mobile SaaS operations → governed data products → predictive AI → decision APIs", fill=MUTED, font=sub_f)
d.line((70, 140, 1530, 140), fill=BORDER, width=2)

boxes = [
    (55, 220, 230, 500, "#2F6FED", "SaaS Operations", ["Web · Android · iOS", "Bookings · Availability", "Services · Ratings", "Payment outcomes"]),
    (310, 220, 485, 500, "#E58A2B", "Data Ingestion", ["Transactional signals", "CDC / event boundary", "Privacy-safe IDs", "Bronze history"]),
    (565, 220, 740, 500, "#6E56CF", "Data Products", ["Standardized entities", "Gold metrics", "Demand features", "Cleaner features"]),
    (820, 220, 995, 500, "#2B9B75", "AI Models", ["Demand forecast", "Cleaner ranking", "Quality guardrails", "Time-aware validation"]),
    (1075, 220, 1250, 500, "#2AA7C9", "Decision API", ["FastAPI", "Forecast endpoint", "Match endpoint", "Stable contracts"]),
    (1330, 220, 1505, 500, "#D65A63", "Consumers", ["Customer app", "Cleaner app", "Operations", "BI / AI"]),
]

for x1, y1, x2, y2, color, title, lines in boxes:
    d.rounded_rectangle((x1, y1, x2, y2), radius=18, fill="white", outline=color, width=3)
    d.rounded_rectangle((x1, y1, x2, y1 + 62), radius=18, fill=color)
    d.rectangle((x1, y1 + 31, x2, y1 + 62), fill=color)
    d.text((x1 + 14, y1 + 18), title, fill="white", font=head_f)
    y = y1 + 92
    for line in lines:
        d.text((x1 + 14, y), line, fill=TEXT, font=body_f)
        y += 38

for x in [230, 485, 740, 995, 1250]:
    d.line((x, 360, x + 80, 360), fill=MUTED, width=4)
    d.polygon([(x + 80, 360), (x + 65, 352), (x + 65, 368)], fill=MUTED)

d.rounded_rectangle((245, 575, 760, 735), radius=18, fill="white", outline="#2F6FED", width=3)
d.text((270, 602), "Governed semantic layer", fill=TEXT, font=font(23, True))
d.text((270, 648), "GMV · completed bookings · cancellation rate", fill=TEXT, font=body_f)
d.text((270, 680), "Supply utilization · explicit definitions · ownership", fill=TEXT, font=body_f)

d.rounded_rectangle((840, 575, 1355, 735), radius=18, fill="white", outline="#6E56CF", width=3)
d.text((865, 602), "Privacy & production mapping", fill=TEXT, font=font(23, True))
d.text((865, 648), "Synthetic public data · no customer PII", fill=TEXT, font=body_f)
d.text((865, 680), "MySQL CDC → Kafka → Snowflake/dbt or Fabric", fill=TEXT, font=body_f)

d.text((70, 810), "BUSINESS VALUE", fill=MUTED, font=font(16, True))
d.text((225, 808), "Demand/supply planning · smarter matching · utilization · conversion · marketplace operations · governed AI", fill=TEXT, font=small_f)

img.save(OUT, format="PNG", optimize=True)
print(f"Generated {OUT} ({OUT.stat().st_size} bytes)")
