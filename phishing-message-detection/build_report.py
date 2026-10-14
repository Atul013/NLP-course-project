"""Build the course report PDF from the editable Markdown source."""

from __future__ import annotations

import re
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Image, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

ROOT = Path(__file__).parent
SOURCE = ROOT / "report/Phishing_Message_Detection_Report.md"
OUTPUT = ROOT / "report/Phishing_Message_Detection_Report.pdf"


def inline(text: str) -> str:
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"`(.+?)`", r"<font name='Courier'>\1</font>", text)
    return text.replace("&", "&amp;").replace("&amp;lt;", "&lt;")


def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.drawString(20 * mm, 12 * mm, "Phishing Message Detection using NLP — Atul Biju")
    canvas.drawRightString(190 * mm, 12 * mm, f"Page {doc.page}")
    canvas.restoreState()


def build() -> None:
    styles = getSampleStyleSheet()
    styles["Heading2"].keepWithNext = True
    styles.add(ParagraphStyle(name="Small", parent=styles["BodyText"], fontSize=8.5, leading=11))
    doc = SimpleDocTemplate(str(OUTPUT), pagesize=A4, rightMargin=20*mm, leftMargin=20*mm, topMargin=18*mm, bottomMargin=20*mm, title="Phishing Message Detection using NLP", author="Atul Biju")
    story = []
    lines = SOURCE.read_text(encoding="utf-8").splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith("# "):
            story.extend([Spacer(1, 35*mm), Paragraph(inline(line[2:]), styles["Title"]), Spacer(1, 8*mm)])
        elif line.startswith("## "):
            # Let Heading2's keepWithNext bind to actual content, not a spacer.
            story.extend([Spacer(1, 3*mm), Paragraph(inline(line[3:]), styles["Heading2"])])
        elif line.startswith("!["):
            image_path = ROOT / "artifacts/confusion_matrix.png"
            story.append(Image(str(image_path), width=95*mm, height=83*mm))
        elif line.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                row = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                if not all(set(c) <= {"-", ":"} for c in row):
                    rows.append(row)
                i += 1
            i -= 1
            table = Table(rows, repeatRows=1, hAlign="LEFT")
            table.setStyle(TableStyle([("BACKGROUND", (0,0), (-1,0), colors.HexColor("#bf4343")), ("TEXTCOLOR", (0,0), (-1,0), colors.white), ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"), ("FONTSIZE", (0,0), (-1,-1), 8), ("GRID", (0,0), (-1,-1), 0.4, colors.grey), ("VALIGN", (0,0), (-1,-1), "TOP"), ("LEFTPADDING", (0,0), (-1,-1), 4), ("RIGHTPADDING", (0,0), (-1,-1), 4)]))
            story.extend([table, Spacer(1, 3*mm)])
        elif re.match(r"^\d+\. ", line):
            story.append(Paragraph(inline(line), styles["BodyText"]))
        elif line and not line.startswith(">"):
            paragraph = line
            while i + 1 < len(lines) and lines[i + 1].strip() and not re.match(r"^(#|\||!\[|\d+\. )", lines[i + 1].strip()):
                i += 1
                paragraph += " " + lines[i].strip()
            story.extend([Paragraph(inline(paragraph), styles["BodyText"]), Spacer(1, 2*mm)])
        i += 1
    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    print(f"Built {OUTPUT}")


if __name__ == "__main__":
    build()
