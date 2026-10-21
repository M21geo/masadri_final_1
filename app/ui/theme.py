"""Colors and sizes shared by every screen (same palette as the design mockups)."""

# Summer palette: warm sand background, ocean-turquoise primary, coral accent, sunny yellow highlights.
# The colours that change between light and dark live in _LIGHT / _DARK; apply() copies one set onto this module.
_LIGHT = dict(BG="#FFF6E5", CARD="#FFFFFF", LINE="#F4E4C8", SOFT="#FFEFD0", INK="#14284B", MUTED="#5A6A85",
              FAINT="#8D9BB3", PRIMARY_SOFT="#D5F3FA", INCOME="#0E9F6E", EXPENSE="#E5484D")
_DARK = dict(BG="#0F1923", CARD="#182634", LINE="#263747", SOFT="#1E2F3F", INK="#EAF2F8", MUTED="#A5B6C8",
             FAINT="#71859A", PRIMARY_SOFT="#123C4D", INCOME="#34D399", EXPENSE="#FF6B70")
BG = CARD = LINE = SOFT = INK = MUTED = FAINT = PRIMARY_SOFT = INCOME = EXPENSE = ""
MODE = "light"

PRIMARY = "#0891B2"
ACCENT = "#FF6B4A"          # floating add button
SUN = "#FFC53D"
HERO = "#0B3C5D"            # dark text colour used on light chips over the hero gradient
HERO_GRAD = ("#0891B2", "#2F6BEA")
HERO_CARD = "#1E5FA8"
HERO_TEXT = "#E4F7FF"
MINT = "#C8FFE0"

TRANSFER = "#3B82F6"

# chart palette: bright but still separable
CHART_INCOME = "#06B6D4"
CHART_EXPENSE = "#FF7A59"
SERIES = ["#06B6D4", "#FF7A59", "#FFC53D", "#8E6CEF", "#FF5C8A", "#2EC27E", "#3A86FF"]
from ..palette import VIVID, vivid  # noqa: E402,F401

TONE = {}   # tone -> (text colour, background); filled by apply()


def _tones(dark: bool) -> dict:
    if dark:
        good, bad, warn, info = ("#7BE5B5", "#12392C"), ("#FF9E9A", "#3D1F24"), ("#FFD27A", "#3A2F12"), ("#7DD8EC", "#123C4D")
    else:
        good, bad, warn, info = ("#0B4A3D", "#D9F7EA"), ("#8A1C12", "#FFE3E1"), ("#7A4A00", "#FFF0C2"), ("#0B3C5D", "#D5F3FA")
    return {"income": (INCOME, good[1]), "expense": (EXPENSE, bad[1]), "neutral": (MUTED, SOFT),
            "good": good, "bad": bad, "warn": warn, "info": info,
            "debt": bad,      # I owe: red
            "owed": warn,     # owed to me: amber
            "paid": good}     # settled / collected: green


def apply(mode: str) -> None:
    """Switch the whole palette ('light' | 'dark'). Screens read T.X when they are built, so redraw afterwards."""
    global MODE
    MODE = "dark" if mode == "dark" else "light"
    globals().update(_DARK if MODE == "dark" else _LIGHT)
    TONE.clear()
    TONE.update(_tones(MODE == "dark"))


def is_dark() -> bool:
    return MODE == "dark"


apply("light")
TONE_ICON = {"good": "#0E9F6E", "warn": "#E0A100", "bad": "#E5484D", "info": "#0891B2"}

DEFAULT_WIDTH = 390  # used until the real window width is known
