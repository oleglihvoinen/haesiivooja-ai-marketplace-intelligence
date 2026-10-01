from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

W, H = 1800, 1080
BG = "#F7F9FC"
TEXT = "#14213D"
MUTED = "#5B6780"
LINE = "#D8E0EC"

OUT = Path(__file__).resolve().parents[1] / "docs" / "architecture.png"
OUT.parent.mkdir(parents=True, exist_ok=True)

def font(size, bold=False):
    paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/dejavu/DejaVuSans.ttf",
    ]
    for path in paths:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            pass
    return ImageFont.load_default()

img = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(img)

d.text((70, 42), "HaeSiivooja Real-Time Marketplace Intelligence & AI Decision Platform",
       fill=TEXT, font=font(36, True))
d.text((70, 92), "Real-time SaaS events → governed data → predictive AI → controlled operational decisions",
       fill=MUTED, font=font(19))
d.line((70, 132, W-70, 132), fill=LINE, width=2)

stage_headers = [
    (55, 155, 405, "#DCEEFF", "1. SaaS & Event Capture"),
    (415, 155, 765, "#DFF6F0", "2. Streaming & Data Platform"),
    (775, 155, 1125, "#EEE7FF", "3. AI & Decision Intelligence"),
    (1135, 155, 1745, "#FFF0E0", "4. Governed Actions & Outcomes"),
]
for x1,y1,x2,color,label in stage_headers:
    d.rounded_rectangle((x1,y1,x2,205), radius=14, fill=color)
    d.text((x1+16,y1+14), label, fill=TEXT, font=font(18,True))

boxes = [
    (45, 255, 235, 555, "#2F6FED", "SaaS Events",
     ["Web · Android · iOS", "Bookings · Search", "Availability", "Ratings · Outcomes"]),
    (255, 255, 445, 555, "#1F9D8A", "MySQL",
     ["Operational source", "Users · Cleaners", "Bookings · Payments", "System of record"]),
    (465, 255, 655, 555, "#6C5CE7", "CDC + Kafka",
     ["Debezium CDC", "Versioned events", "Real-time streams", "Replay boundary"]),
    (675, 255, 865, 555, "#E88924", "Bronze / Silver",
     ["Immutable history", "Deduplication", "Conformed entities", "Data quality"]),
    (885, 255, 1075, 555, "#D4A017", "Gold + Features",
     ["Governed metrics", "Feature tables", "Supply / demand", "Semantic contracts"]),
    (1095, 255, 1285, 555, "#8E44AD", "ML Models",
     ["Demand forecast", "Cleaner ranking", "Anomaly signals", "Model monitoring"]),
    (1305, 255, 1495, 555, "#18A999", "AI Decision",
     ["Gap detection", "Recommendations", "Policy guardrails", "Human approval"]),
    (1515, 255, 1705, 555, "#D95763", "Actions + Apps",
     ["Action APIs", "Campaigns", "Notifications", "Web / mobile UX"]),
]

for x1,y1,x2,y2,color,title,lines in boxes:
    d.rounded_rectangle((x1,y1,x2,y2), radius=18, fill="white", outline=color, width=3)
    d.rounded_rectangle((x1,y1,x2,y1+62), radius=18, fill=color)
    d.rectangle((x1,y1+31,x2,y1+62), fill=color)
    d.text((x1+14,y1+18), title, fill="white", font=font(19,True))
    yy=y1+95
    for line in lines:
        d.text((x1+14,yy), line, fill=TEXT, font=font(16))
        yy += 42

for x in [235,445,655,865,1075,1285,1495]:
    d.line((x,405,x+20,405), fill=MUTED, width=4)
    d.polygon([(x+20,405),(x+10,398),(x+10,412)], fill=MUTED)

# Feedback loop
d.line((1600,590,1600,645), fill="#5A4FCF", width=5)
d.line((1600,645,145,645), fill="#5A4FCF", width=5)
d.line((145,645,145,590), fill="#5A4FCF", width=5)
d.polygon([(145,590),(136,605),(154,605)], fill="#5A4FCF")
d.rounded_rectangle((610,615,1190,675), radius=25, fill="#EAE5FF")
d.text((650,632), "Outcome events · conversion · capacity · quality · measured impact",
       fill="#4638A8", font=font(17,True))

# Supporting controls
supports=[
    (70,725,560,925,"#DCEEFF","#2477D4","Operational Decisions",
     ["Supply-demand gap detection","Availability campaigns","Incentive simulation","Matching optimization"]),
    (655,725,1145,925,"#DFF6F0","#118A7E","Observability & Reliability",
     ["Data quality & freshness","Kafka lag / SLA","Model & decision monitoring","Lineage and provenance"]),
    (1240,725,1730,925,"#EEE7FF","#7447C6","Privacy & Security",
     ["Pseudonymous IDs","GDPR controls","Access policies","Audit trail / approvals"]),
]
for x1,y1,x2,y2,fill,accent,title,lines in supports:
    d.rounded_rectangle((x1,y1,x2,y2), radius=18, fill=fill, outline=accent, width=2)
    d.text((x1+22,y1+22), title, fill=TEXT, font=font(21,True))
    yy=y1+68
    for line in lines:
        d.ellipse((x1+24,yy+7,x1+34,yy+17), fill=accent)
        d.text((x1+48,yy), line, fill=TEXT, font=font(16))
        yy += 34

# Closed-loop bar
d.rounded_rectangle((70,965,1730,1035), radius=22, fill="#133C6B")
d.text((95,986), "CLOSED-LOOP INTELLIGENCE", fill="white", font=font(18,True))
d.text((425,986), "Observe  →  Predict  →  Recommend  →  Approve  →  Act  →  Measure  →  Improve",
       fill="white", font=font(18,True))

img.save(OUT, format="PNG", optimize=True)
print(f"Generated {OUT} ({OUT.stat().st_size} bytes)")
