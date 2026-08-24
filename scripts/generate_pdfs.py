from __future__ import annotations

import html
import re
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    KeepTogether,
    ListFlowable,
    ListItem,
    PageBreak,
    Paragraph,
    Preformatted,
    SimpleDocTemplate,
    Spacer,
)


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "output" / "pdf"
ACCENT = colors.HexColor("#00A7A5")
NAVY = colors.HexColor("#102A43")
MUTED = colors.HexColor("#52606D")
PALE = colors.HexColor("#EAF7F6")

DOCUMENTS = (
    ("docs/relatorio-mvp.md", "relatorio-mvp.pdf", "MVP conversacional e integração Watson"),
    (
        "docs/relatorio-ia-generativa.md",
        "relatorio-ia-generativa.pdf",
        "Ir Além 1 — extração estruturada com Gemini",
    ),
    ("docs/relatorio-rpa.md", "relatorio-rpa.pdf", "Ir Além 2 — automação e dados híbridos"),
)


def register_fonts() -> tuple[str, str, str]:
    fonts_dir = Path("C:/Windows/Fonts")
    regular = fonts_dir / "arial.ttf"
    bold = fonts_dir / "arialbd.ttf"
    mono = fonts_dir / "consola.ttf"
    if regular.exists() and bold.exists() and mono.exists():
        pdfmetrics.registerFont(TTFont("CardioSans", str(regular)))
        pdfmetrics.registerFont(TTFont("CardioSansBold", str(bold)))
        pdfmetrics.registerFont(TTFont("CardioMono", str(mono)))
        return "CardioSans", "CardioSansBold", "CardioMono"
    return "Helvetica", "Helvetica-Bold", "Courier"


REGULAR, BOLD, MONO = register_fonts()


def styles() -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "CardioTitle",
            parent=base["Title"],
            fontName=BOLD,
            fontSize=21,
            leading=24,
            textColor=NAVY,
            alignment=TA_LEFT,
            spaceAfter=5 * mm,
        ),
        "subtitle": ParagraphStyle(
            "CardioSubtitle",
            parent=base["Normal"],
            fontName=REGULAR,
            fontSize=9,
            leading=12,
            textColor=MUTED,
            backColor=PALE,
            borderColor=ACCENT,
            borderWidth=0.8,
            borderPadding=8,
            spaceAfter=5 * mm,
        ),
        "h2": ParagraphStyle(
            "CardioH2",
            parent=base["Heading2"],
            fontName=BOLD,
            fontSize=12.5,
            leading=15,
            textColor=NAVY,
            spaceBefore=3.2 * mm,
            spaceAfter=1.8 * mm,
            keepWithNext=True,
        ),
        "body": ParagraphStyle(
            "CardioBody",
            parent=base["BodyText"],
            fontName=REGULAR,
            fontSize=9,
            leading=12.4,
            textColor=colors.HexColor("#243B53"),
            alignment=TA_LEFT,
            spaceAfter=2.2 * mm,
        ),
        "bullet": ParagraphStyle(
            "CardioBullet",
            parent=base["BodyText"],
            fontName=REGULAR,
            fontSize=8.8,
            leading=12,
            textColor=colors.HexColor("#243B53"),
        ),
        "code": ParagraphStyle(
            "CardioCode",
            parent=base["Code"],
            fontName=MONO,
            fontSize=7.3,
            leading=9.5,
            textColor=colors.HexColor("#102A43"),
            backColor=colors.HexColor("#F0F4F8"),
            borderColor=colors.HexColor("#BCCCDC"),
            borderWidth=0.5,
            borderPadding=7,
            spaceBefore=1.5 * mm,
            spaceAfter=3 * mm,
        ),
        "footer": ParagraphStyle(
            "CardioFooter",
            parent=base["Normal"],
            fontName=REGULAR,
            fontSize=7.5,
            leading=9,
            textColor=MUTED,
            alignment=TA_CENTER,
        ),
    }


STYLES = styles()


def inline_markup(value: str) -> str:
    escaped = html.escape(value, quote=False)
    return re.sub(r"`([^`]+)`", rf'<font name="{MONO}">\1</font>', escaped)


def parse_markdown(text: str, subtitle: str) -> list:
    lines = text.splitlines()
    story: list = []
    paragraph: list[str] = []
    bullets: list[str] = []
    code: list[str] = []
    in_code = False
    title_written = False

    def flush_paragraph() -> None:
        if paragraph:
            story.append(Paragraph(inline_markup(" ".join(paragraph)), STYLES["body"]))
            paragraph.clear()

    def flush_bullets() -> None:
        if bullets:
            items = [
                ListItem(Paragraph(inline_markup(item), STYLES["bullet"]), leftIndent=3 * mm)
                for item in bullets
            ]
            story.append(
                ListFlowable(
                    items,
                    bulletType="bullet",
                    start="circle",
                    bulletColor=ACCENT,
                    leftIndent=5 * mm,
                    bulletFontName=BOLD,
                    spaceAfter=2.5 * mm,
                )
            )
            bullets.clear()

    for raw in lines:
        stripped = raw.strip()
        if stripped.startswith("```"):
            flush_paragraph()
            flush_bullets()
            if in_code:
                story.append(Preformatted("\n".join(code), STYLES["code"])); code.clear()
            in_code = not in_code
            continue
        if in_code:
            code.append(raw)
            continue
        if stripped.startswith("# ") and not title_written:
            flush_paragraph(); flush_bullets()
            story.append(Paragraph(inline_markup(stripped[2:]), STYLES["title"]))
            story.append(
                Paragraph(
                    f"{inline_markup(subtitle)}<br/><font color='#52606D'>"
                    "Projeto acadêmico • 24/08/2026 • execução oficial em Docker</font>",
                    STYLES["subtitle"],
                )
            )
            title_written = True
            continue
        if stripped.startswith("## "):
            flush_paragraph(); flush_bullets()
            story.append(Paragraph(inline_markup(stripped[3:]), STYLES["h2"]))
            continue
        if stripped.startswith("- "):
            flush_paragraph()
            bullets.append(stripped[2:])
            continue
        if not stripped:
            flush_paragraph(); flush_bullets()
            continue
        paragraph.append(stripped)

    flush_paragraph(); flush_bullets()
    if code:
        story.append(Preformatted("\n".join(code), STYLES["code"]))
    story.append(Spacer(1, 2 * mm))
    story.append(
        KeepTogether(
            [
                Paragraph(
                    "Limite de uso: demonstração acadêmica com dados fictícios; "
                    "toda saída requer revisão humana.",
                    STYLES["subtitle"],
                )
            ]
        )
    )
    return story


def decorate(canvas, document) -> None:
    width, height = A4
    canvas.saveState()
    canvas.setFillColor(NAVY)
    canvas.rect(0, height - 12 * mm, width, 12 * mm, fill=1, stroke=0)
    canvas.setFillColor(ACCENT)
    canvas.rect(0, height - 12.8 * mm, width, 0.8 * mm, fill=1, stroke=0)
    canvas.setFillColor(colors.white)
    canvas.setFont(BOLD, 8.5)
    canvas.drawString(17 * mm, height - 7.8 * mm, "CARDIOIA")
    canvas.setStrokeColor(colors.HexColor("#D9E2EC"))
    canvas.line(17 * mm, 14 * mm, width - 17 * mm, 14 * mm)
    canvas.setFillColor(MUTED)
    canvas.setFont(REGULAR, 7.5)
    canvas.drawString(17 * mm, 9.5 * mm, "FIAP • Fase 5 • cenário exclusivamente fictício")
    canvas.drawRightString(width - 17 * mm, 9.5 * mm, f"Página {document.page}")
    canvas.restoreState()


def build(source: Path, target: Path, subtitle: str) -> None:
    document = SimpleDocTemplate(
        str(target),
        pagesize=A4,
        rightMargin=17 * mm,
        leftMargin=17 * mm,
        topMargin=21 * mm,
        bottomMargin=18 * mm,
        title=subtitle,
        author="Equipe CardioIA",
        subject="Projeto acadêmico FIAP — Fase 5",
    )
    document.build(
        parse_markdown(source.read_text(encoding="utf-8"), subtitle),
        onFirstPage=decorate,
        onLaterPages=decorate,
    )


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for source_name, target_name, subtitle in DOCUMENTS:
        build(ROOT / source_name, OUTPUT_DIR / target_name, subtitle)
        print(f"generated={target_name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
