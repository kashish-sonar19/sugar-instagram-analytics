"""Colours, Altair styling and small UI helpers (dark theme)."""

import altair as alt
import streamlit as st

BG = "#111214"
SURFACE = "#1a1a19"
INK = "#f0efec"
INK_2 = "#c3c2b7"
GRID = "#2c2c2a"
AXIS = "#383835"

ACCENT = "#199e70"        # single-series colour (aqua)
ACCENT_HI = "#2fd49a"     # highlighted / selected
MUTED = "#2e4a40"         # de-selected
NEG = "#d95926"           # below-average deviation

FORMAT_COLORS = {"Image": "#199e70", "Reel": "#c98500", "Story": "#9085e9", "Video": "#d55181"}
FORMAT_SCALE = alt.Scale(domain=list(FORMAT_COLORS), range=list(FORMAT_COLORS.values()))
SEQ = ["#0f3d2e", "#146b4f", "#199e70", "#5cc79f", "#a6e6cd"]   # dark -> light aqua ramp


def altair_theme():
    return {
        "config": {
            "background": SURFACE,
            "padding": {"left": 10, "right": 14, "top": 10, "bottom": 10},
            "view": {"stroke": None},
            "font": "Inter, Segoe UI, sans-serif",
            "title": {"color": INK, "fontSize": 15, "fontWeight": 600, "anchor": "start", "offset": 12},
            "axis": {"labelColor": INK_2, "titleColor": INK_2, "gridColor": GRID, "domainColor": AXIS,
                     "tickColor": AXIS, "labelFontSize": 12, "titleFontSize": 12, "titleFontWeight": 500},
            "legend": {"labelColor": INK_2, "titleColor": INK_2, "orient": "top", "labelFontSize": 12},
            "bar": {"cornerRadiusEnd": 4},
            "text": {"color": INK, "fontSize": 12},
            "line": {"strokeWidth": 2},
            "point": {"size": 70, "filled": True},
        }
    }


def register():
    alt.data_transformers.disable_max_rows()
    try:  # Altair 5.5+
        alt.theme.register("kashish_dark", enable=True)(altair_theme)
    except AttributeError:  # older Altair 5
        alt.themes.register("kashish_dark", altair_theme)
        alt.themes.enable("kashish_dark")


CSS = f"""
<style>
.block-container {{padding-top: 2rem; max-width: 1400px;}}
.kcard {{background:{SURFACE}; border:1px solid {GRID}; border-radius:14px; padding:16px 18px;}}
.kcard .k {{color:{INK_2}; font-size:.8rem; text-transform:uppercase; letter-spacing:.06em;}}
.kcard .v {{color:{INK}; font-size:1.75rem; font-weight:700; margin-top:4px;}}
.kcard .s {{color:{INK_2}; font-size:.78rem; margin-top:2px;}}
.takeaway {{background:#132a22; border:1px solid #1f4a3a; border-radius:12px; padding:12px 16px;
            color:{INK}; margin:4px 0 18px 0; font-size:.93rem;}}
.takeaway b {{color:{ACCENT_HI};}}
.pagehead {{color:{INK_2}; font-size:.9rem; margin-top:-8px; margin-bottom:12px;}}
</style>
"""


def inject_css():
    st.markdown(CSS, unsafe_allow_html=True)


def kpi_cards(items):
    """items: list of (label, value, sub)"""
    cols = st.columns(len(items))
    for col, (label, value, sub) in zip(cols, items):
        col.markdown(f"<div class='kcard'><div class='k'>{label}</div><div class='v'>{value}</div>"
                     f"<div class='s'>{sub}</div></div>", unsafe_allow_html=True)


def takeaway(html):
    st.markdown(f"<div class='takeaway'>✅ <b>Takeaway:</b> {html}</div>", unsafe_allow_html=True)


def header(title, subtitle=""):
    st.title(title)
    if subtitle:
        st.markdown(f"<div class='pagehead'>{subtitle}</div>", unsafe_allow_html=True)


def human(n, digits=1):
    n = float(n)
    for div, suf in ((1e9, "B"), (1e6, "M"), (1e3, "K")):
        if abs(n) >= div:
            return f"{n / div:.{digits}f}{suf}"
    return f"{n:,.0f}"
