from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from genai.extractor import DeterministicExtractor, GeminiExtractor


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(
        description="Extrai dados de um cenário clínico exclusivamente fictício."
    )
    result.add_argument("--mode", choices=("deterministic", "gemini"), default="deterministic")
    result.add_argument("--input-file", required=True)
    result.add_argument("--output-file")
    return result


def main() -> int:
    args = parser().parse_args()
    source = Path(args.input_file).read_text(encoding="utf-8")
    if args.mode == "gemini":
        extractor = GeminiExtractor(
            api_key=os.getenv("GEMINI_API_KEY", ""),
            model=os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite"),
        )
    else:
        extractor = DeterministicExtractor()

    output = extractor.extract(source).model_dump_json(indent=2)
    if args.output_file:
        Path(args.output_file).write_text(output + "\n", encoding="utf-8")
    else:
        print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
