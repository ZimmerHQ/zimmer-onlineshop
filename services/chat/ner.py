import re
from typing import Optional, List
from .state import Slots

# Basic Persian NER for MVP: extract size (integer 18-60) and color (from palette).
# Expand palette as needed.
DEFAULT_COLORS = ["مشکی","سفید","آبی","قرمز","سبز","خاکستری","بژ","قهوه‌ای","سرمه‌ای","زیتونی"]

DIGIT_MAP = {
    "۰":"0","۱":"1","۲":"2","۳":"3","۴":"4","۵":"5","۶":"6","۷":"7","۸":"8","۹":"9",
    "٠":"0","١":"1","٢":"2","٣":"3","٤":"4","٥":"5","٦":"6","٧":"7","٨":"8","٩":"9"
}

def _normalize_digits(text: str) -> str:
    return "".join(DIGIT_MAP.get(ch, ch) for ch in text or "")

def extract_slots(text: str, color_palette: Optional[List[str]] = None) -> Slots:
    if color_palette is None:
        color_palette = DEFAULT_COLORS
    t = (text or "").strip()
    t_norm = _normalize_digits(t)

    # size: first integer 18-60
    size = None
    for m in re.finditer(r"(?<!\d)(\d{2})(?!\d)", t_norm):
        val = int(m.group(1))
        if 18 <= val <= 60:
            size = str(val)
            break

    # color: first matching token from palette
    color = None
    for c in color_palette:
        if c in t:
            color = c
            break

    # qty (optional): phrases like "دو تا" not covered; MVP uses default 1
    return Slots(size=size, color=color, qty=1) 