from pathlib import Path


def load_system_prompt(path: str, fallback: str | None = None) -> str | None:
    p = Path(path)
    if p.exists():
        return p.read_text(encoding="utf-8").strip()

    return fallback
