from __future__ import annotations

import os
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
FRAMES = Path(os.getenv("VIDEO_FRAMES_DIR", ROOT / "output" / "video" / "frames"))
WIDTH, HEIGHT = 1280, 720
NAVY = "#102A43"
TEAL = "#00A7A5"
WHITE = "#FFFFFF"
PALE = "#EAF7F6"
MUTED = "#B8C7D1"


def font(size: int, *, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = (
        Path("C:/Windows/Fonts") / ("arialbd.ttf" if bold else "arial.ttf"),
        Path("/usr/share/fonts/dejavu")
        / ("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"),
    )
    selected = next((candidate for candidate in candidates if candidate.exists()), None)
    if selected is None:
        raise RuntimeError("Fonte compatível não encontrada.")
    return ImageFont.truetype(str(selected), size)


def centered(draw: ImageDraw.ImageDraw, text: str, y: int, selected_font, fill: str) -> None:
    box = draw.textbbox((0, 0), text, font=selected_font)
    x = (WIDTH - (box[2] - box[0])) // 2
    draw.text((x, y), text, font=selected_font, fill=fill)


def title_frame() -> Image.Image:
    image = Image.new("RGB", (WIDTH, HEIGHT), NAVY)
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, WIDTH, 12), fill=TEAL)
    centered(draw, "CARDIOIA", 160, font(74, bold=True), WHITE)
    centered(
        draw,
        "Demonstração real • Docker + IBM Watson Assistant",
        265,
        font(31),
        PALE,
    )
    centered(draw, "FIAP • Fase 5 • cenário exclusivamente fictício", 330, font(24), MUTED)
    draw.rounded_rectangle((225, 420, 1055, 535), radius=18, fill="#173F5F", outline=TEAL, width=2)
    centered(draw, "Não diagnostica • não prescreve • exige revisão humana", 455, font(25, bold=True), WHITE)
    return image


def final_frame() -> Image.Image:
    image = Image.new("RGB", (WIDTH, HEIGHT), WHITE)
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, WIDTH, 110), fill=NAVY)
    draw.rectangle((0, 110, WIDTH, 118), fill=TEAL)
    centered(draw, "VALIDAÇÃO CONCLUÍDA", 32, font(40, bold=True), WHITE)

    items = (
        "9 casos reais do Watson aprovados",
        "13 testes unitários + 9 smoke tests",
        "12 testes GenAI + chamada Gemini real",
        "13 verificações do fluxo RPA híbrido",
    )
    y = 185
    for item in items:
        draw.ellipse((205, y + 9, 225, y + 29), fill=TEAL)
        draw.text((250, y), item, font=font(29), fill=NAVY)
        y += 75

    draw.rounded_rectangle((180, 530, 1100, 625), radius=16, fill=PALE, outline=TEAL, width=2)
    centered(draw, "github.com/FelipeLivino/fiap_fase5", 558, font(28, bold=True), NAVY)
    centered(draw, "Execução oficial em Docker Compose", 655, font(21), "#52606D")
    return image


def normalize_browser_frames() -> int:
    """Converte capturas do navegador para PNG real, independentemente do codec de origem."""
    converted = 0
    generated = {"00-titulo.png", "12-encerramento.png"}
    for path in sorted(FRAMES.glob("[0-9][0-9]-*.png")):
        if path.name in generated:
            continue
        with Image.open(path) as source:
            normalized = source.convert("RGB")
        temporary = path.with_suffix(".normalized.png")
        normalized.save(temporary, format="PNG", optimize=True)
        temporary.replace(path)
        converted += 1
    return converted


def main() -> int:
    FRAMES.mkdir(parents=True, exist_ok=True)
    normalized = normalize_browser_frames()
    title_frame().save(FRAMES / "00-titulo.png")
    final_frame().save(FRAMES / "12-encerramento.png")
    print(f"video_assets=generated count=2 normalized_browser_frames={normalized}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
