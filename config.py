"""Shared path configuration — auto-detects Google Colab vs local machine."""

from __future__ import annotations

from pathlib import Path

# --- Google Colab (Drive) paths — data folders on Shared Drive ---
COLAB_DRIVE_BASE = (
    "/content/drive/Shareddrives/FA Ops Europe: Rate Maintenance Team "
    "/Documents/AI Adoption RMT/RMT_APTIV_VERSIGENT/RMT_Road"
)
COLAB_INPUT_DIR = f"{COLAB_DRIVE_BASE}/input"
COLAB_OUTPUT_DIR = f"{COLAB_DRIVE_BASE}/output"
COLAB_PROCESSING_DIR = f"{COLAB_DRIVE_BASE}/processing"

# Active layout keys (see converters/__init__.py LAYOUT_LABELS for display names)
LAYOUTS: tuple[str, ...] = ("usual_rate", "new_grid")

# Old input/processing folder names still scanned if present
LEGACY_INPUT_FOLDERS: dict[str, tuple[str, ...]] = {
    "usual_rate": ("layout1", "layout2", "layout4"),
    "new_grid": ("layout3",),
}


def _is_colab() -> bool:
    try:
        import google.colab  # noqa: F401

        return True
    except ImportError:
        return False


IS_COLAB = _is_colab()

_SCRIPT_ROOT = Path(__file__).resolve().parent
_DRIVE_INPUT = Path(COLAB_INPUT_DIR)

if IS_COLAB and _DRIVE_INPUT.is_dir():
    PROJECT_ROOT = _SCRIPT_ROOT
    INPUT_DIR = _DRIVE_INPUT
    OUTPUT_DIR = Path(COLAB_OUTPUT_DIR)
    PROCESSING_DIR = Path(COLAB_PROCESSING_DIR)
else:
    PROJECT_ROOT = _SCRIPT_ROOT
    INPUT_DIR = PROJECT_ROOT / "input"
    OUTPUT_DIR = PROJECT_ROOT / "output"
    PROCESSING_DIR = PROJECT_ROOT / "processing"


def normalize_layout(layout: str) -> str:
    """Map legacy layout1–layout4 names to usual_rate / new_grid."""
    from converters import LEGACY_LAYOUT_ALIASES

    return LEGACY_LAYOUT_ALIASES.get(layout, layout)


def input_dirs_for(layout: str) -> list[Path]:
    """Input folders to scan (new name + any legacy folder names on disk)."""
    key = normalize_layout(layout)
    seen: set[Path] = set()
    dirs: list[Path] = []
    for name in (key, layout, *LEGACY_INPUT_FOLDERS.get(key, ())):
        p = (INPUT_DIR / name).resolve()
        if p in seen:
            continue
        seen.add(p)
        if p.is_dir():
            dirs.append(p)
    if not dirs:
        dirs.append(INPUT_DIR / key)
    return dirs


def ensure_dirs() -> None:
    """Create processing/ and output/ trees (including per-layout subfolders)."""
    for base in (PROCESSING_DIR, OUTPUT_DIR):
        base.mkdir(parents=True, exist_ok=True)
        for layout in LAYOUTS:
            (base / layout).mkdir(parents=True, exist_ok=True)


def matrix_output_path(converted_path: Path) -> Path:
    """Mirror processing/<layout>/… under output/<layout>/… for matrix files."""
    stem = converted_path.stem.replace("_converted", "") + "_matrix.xlsx"
    try:
        rel = converted_path.resolve().relative_to(PROCESSING_DIR.resolve())
        if len(rel.parts) > 1:
            return OUTPUT_DIR / rel.parent / stem
    except ValueError:
        pass
    return OUTPUT_DIR / stem
