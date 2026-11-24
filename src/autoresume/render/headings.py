"""FR/EN headings for skill categories (docs/decisions/2026-11-24-category-headings-table.md)."""

import logging

logger = logging.getLogger(__name__)

# category id -> (EN heading, FR heading)
CATEGORY_HEADINGS: dict[str, tuple[str, str]] = {
    "audio": ("Audio", "Audio"),
    "ml": ("Machine learning", "Machine learning"),
    "mlops": ("MLOps & engineering", "MLOps et ingénierie"),
    "programming": ("Programming", "Programmation"),
    "music": ("Music", "Musique"),
    "languages": ("Languages", "Langues"),
    "data": ("Data", "Données"),
}


def category_heading(category: str, lang: str) -> str:
    """Return the heading of `category` in `lang` ("fr" or "en").

    An unknown category gets a tidied id ("soft-skills" -> "Soft skills") and a warning.
    """
    entry = CATEGORY_HEADINGS.get(category)
    if entry is not None:
        return entry[1] if lang == "fr" else entry[0]
    logger.warning("no heading for skill category %r: using a tidied id", category)
    tidy = category.replace("-", " ")
    return tidy[:1].upper() + tidy[1:]
