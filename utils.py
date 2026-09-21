"""
utils.py
--------
Shared code used across all pages of the multi-page dashboard:
styling, model/data loading, and Zameen scraping helpers.
"""

import re

import joblib
import pandas as pd
import requests
import streamlit as st
from bs4 import BeautifulSoup

ALL_CITIES = ["Gujrat", "Gujranwala", "Sialkot", "Jhelum", "Wazirabad"]

PRICE_RE = re.compile(r"PKR\s*([\d,.]+)\s*(Crore|Lakh|Lac|Arab)?", re.IGNORECASE)
SIZE_RE = re.compile(r"(\d+(?:\.\d+)?)\s*(Marla|Kanal)", re.IGNORECASE)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}

# ----------------------------------------------------------------------
# Shared CSS — dark green + gold, Sora + Inter typography
# ----------------------------------------------------------------------
CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@600;700&family=Inter:wght@400;500;600;700&display=swap');
@import url('https://cdnjs.cloudflare.com/ajax/libs/tabler-icons/2.44.0/iconfont/tabler-icons.min.css');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background-color: #F3ECF7;
}
[data-testid="stAppViewContainer"] {
    background-color: #F3ECF7;
}
[data-testid="stHeader"] {
    background-color: rgba(0, 0, 0, 0);
}

.block-container {
    max-width: 800px;
    padding-top: 2.5rem;
    padding-bottom: 3rem;
}

/* ---------------- Sidebar navigation ---------------- */
section[data-testid="stSidebar"] {
    background-color: #3E2A5E;
    border-right: none;
}
section[data-testid="stSidebar"] > div {
    padding-top: 1.5rem;
}
[data-testid="stSidebarNav"] {
    padding-top: 0.5rem;
}
[data-testid="stSidebarNav"] a {
    color: #D9CBEA !important;
    font-family: 'Inter', sans-serif;
    font-weight: 500;
    font-size: 0.92rem;
    border-radius: 8px;
    margin: 2px 8px;
    padding: 0.5rem 0.8rem !important;
    transition: background-color 0.15s ease, color 0.15s ease;
}
[data-testid="stSidebarNav"] a:hover {
    background-color: #573875;
    color: #F3ECF7 !important;
}
[data-testid="stSidebarNav"] a[aria-current="page"] {
    background-color: #D4AF37 !important;
    color: #3E2A5E !important;
    font-weight: 700;
}
[data-testid="stSidebarNav"] span {
    color: inherit !important;
}
[data-testid="stSidebarNav"] > ul > li:first-child span::before {
    content: "🏠  ";
}
[data-testid="stSidebarNavSeparator"] {
    border-color: #2C1F42 !important;
}

/* Header */
.app-header {
    background-color: #3E2A5E;
    border-radius: 12px;
    padding: 1.6rem 1.9rem;
    display: flex;
    align-items: center;
    gap: 14px;
    margin-bottom: 2rem;
    box-shadow: 0 4px 14px rgba(62, 42, 94, 0.18);
}
.app-header .icon-mark {
    width: 42px; height: 42px;
    background-color: #D4AF37;
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    flex-shrink: 0;
    font-size: 22px;
}
.app-header .title {
    font-family: 'Sora', sans-serif;
    font-size: 20px; font-weight: 700; line-height: 1.2;
}
.app-header .title .light { color: #F3ECF7; }
.app-header .title .gold { color: #D4AF37; }
.app-header .subtitle {
    font-size: 11px; color: #C4AFDA; margin-top: 3px; letter-spacing: 0.3px;
}

/* Input boxes */
.input-label {
    font-size: 11px; color: #7A6B8C; font-weight: 600; margin-bottom: 6px;
    letter-spacing: 0.3px;
}
div[data-testid="stSelectbox"] > div > div,
div[data-testid="stNumberInput"] > div > div,
div[data-testid="stTextInput"] > div > div {
    background-color: #FBF8FD;
    border: 1.5px solid #DDD0E8 !important;
    border-radius: 10px !important;
}

/* Buttons */
.stButton button {
    width: 100%;
    background-color: #3E2A5E;
    color: #D4AF37 !important;
    border: none;
    border-radius: 10px;
    padding: 0.7rem 1rem;
    font-family: 'Sora', sans-serif;
    font-weight: 600;
    font-size: 0.95rem;
    transition: background-color 0.2s ease, transform 0.15s ease;
}
.stButton button:hover {
    background-color: #573875;
    transform: translateY(-1px);
}

/* Secondary (outline) button — used for reset/refresh actions */
.stButton button[kind="secondary"] {
    background-color: #FFFFFF !important;
    color: #3E2A5E !important;
    border: 1.5px solid #DDD0E8 !important;
}
.stButton button[kind="secondary"]:hover {
    background-color: #FBF8FD !important;
    border-color: #3E2A5E !important;
    transform: none;
}

/* Result card */
.result-card {
    background-color: #FFFFFF;
    border: 1px solid #E9DFF2;
    border-left: 5px solid #D4AF37;
    border-radius: 12px;
    padding: 1.8rem;
    margin-bottom: 1.3rem;
    box-shadow: 0 2px 10px rgba(62, 42, 94, 0.08);
    animation: fadeSlideUp 0.45s ease-out;
}
@keyframes fadeSlideUp {
    from { opacity: 0; transform: translateY(12px); }
    to   { opacity: 1; transform: translateY(0); }
}
.result-label { font-size: 12px; color: #7A6B8C; margin-bottom: 6px; }
.result-price {
    font-family: 'Sora', sans-serif;
    font-size: 38px; font-weight: 700; color: #3E2A5E;
}
.result-price .gold { color: #B8912C; }
.result-raw { font-size: 12px; color: #A897BA; margin-top: 6px; }

/* Section cards */
.section-card {
    background-color: #FFFFFF;
    border: 1px solid #E9DFF2;
    border-radius: 12px;
    padding: 1.4rem 1.7rem;
    margin-bottom: 1.3rem;
    box-shadow: 0 2px 10px rgba(62, 42, 94, 0.06);
}
.section-title {
    font-family: 'Sora', sans-serif;
    font-size: 13px; font-weight: 600; color: #3E2A5E; margin: 2rem 0 0.9rem 0;
}
.listing-row {
    display: flex; justify-content: space-between; align-items: center;
    font-size: 13px; color: #5A4B70; padding: 9px 0;
    border-bottom: 1px solid #F2EAF8;
}
.listing-row:last-child { border-bottom: none; }
.listing-price { color: #B8912C; font-weight: 600; }

/* Deal verdict badges */
.verdict-badge {
    display: inline-block;
    padding: 7px 16px;
    border-radius: 20px;
    font-family: 'Sora', sans-serif;
    font-weight: 700;
    font-size: 13px;
    margin-bottom: 12px;
}
.verdict-good { background-color: #E3F3E9; color: #1E7A46; }
.verdict-fair { background-color: #F3F0E3; color: #8A7A1E; }
.verdict-bad { background-color: #F8E5E5; color: #A62B2B; }

/* Footer */
.app-footer {
    display: flex;
    align-items: center;
    gap: 12px;
    background-color: #FFFFFF;
    border: 1px solid #E9DFF2;
    border-radius: 12px;
    padding: 1rem 1.3rem;
    margin-top: 2.5rem;
}
.app-footer-icon {
    width: 32px; height: 32px;
    background-color: #F3ECF7;
    border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    flex-shrink: 0;
    font-size: 16px;
}
.app-footer-title {
    font-family: 'Sora', sans-serif;
    font-size: 12.5px; font-weight: 700; color: #3E2A5E;
}
.app-footer-sub {
    font-size: 11.5px; color: #9A8CB0; margin-top: 2px;
}

/* Empty-state placeholder card */
.empty-state {
    background-color: #FFFFFF;
    border: 1.5px dashed #DDD0E8;
    border-radius: 12px;
    padding: 2.2rem 1.8rem;
    text-align: center;
    margin-top: 0.5rem;
}
.empty-state .emoji { font-size: 32px; margin-bottom: 0.6rem; }
.empty-state .msg { font-size: 13.5px; color: #5A4B70; line-height: 1.6; }
.empty-state .msg b { color: #3E2A5E; }
/* Sidebar collapse/expand arrow — make visible on dark background */
/* Sidebar collapse/expand arrow — make visible on dark background
   (using a wildcard match since Streamlit renames this test-id across versions) */
section[data-testid="stSidebar"] [data-testid*="ollapse" i],
section[data-testid="stSidebar"] [data-testid*="ollapse" i] button {
    background-color: rgba(255, 255, 255, 0.28) !important;
    border-radius: 8px !important;
}
section[data-testid="stSidebar"] [data-testid*="ollapse" i] svg {
    color: #FFFFFF !important;
    fill: #FFFFFF !important;
    opacity: 1 !important;
}

/* Sidebar brand mark (rendered manually via render_sidebar_brand) */
.sidebar-brand {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 0 14px 1.2rem 14px;
    margin-bottom: 0.5rem;
    border-bottom: 1px solid #4F3570;
}
.sidebar-brand .icon-mark {
    width: 32px; height: 32px;
    background-color: #D4AF37;
    border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    flex-shrink: 0;
    font-size: 16px;
}
.sidebar-brand .brand-text {
    font-family: 'Sora', sans-serif;
    font-size: 14px; font-weight: 700; color: #F5F1E8; line-height: 1.2;
}
.sidebar-brand .brand-text .gold { color: #D4AF37; }

/* Card hover lift */
.section-card, .stat-card {
    transition: transform 0.15s ease, box-shadow 0.15s ease;
}
.section-card:hover, .stat-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 18px rgba(62, 42, 94, 0.12);
}
.stat-card {
    background-color: #FBF8FD;
    border: 1px solid #E9DFF2;
    border-radius: 12px;
    padding: 1.1rem 1.2rem;
    text-align: center;
}
.stat-value {
    font-family: 'Sora', sans-serif;
    font-size: 24px; font-weight: 700; color: #3E2A5E;
}
.stat-label { font-size: 11px; color: #7A6B8C; margin-top: 4px; }
</style>
"""


def apply_page_config(page_title):
    st.set_page_config(page_title=page_title, page_icon="🏠", layout="wide")
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def render_header():
    st.markdown(
        """
        <div class="app-header">
            <div class="icon-mark">🏠</div>
            <div>
                <div class="title"><span class="light">House Price</span> <span class="gold">Predictor</span></div>
                <div class="subtitle">GUJRAT · GUJRANWALA · SIALKOT · JHELUM · WAZIRABAD</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    render_sidebar_brand()


def render_sidebar_brand():
    with st.sidebar:
        st.markdown(
            """
            <div class="sidebar-brand">
                <div class="icon-mark">🏠</div>
                <div class="brand-text">House Price <span class="gold">Predictor</span></div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_footer():
    st.markdown(
        """
        <div class="app-footer">
            <div class="app-footer-icon">🏠</div>
            <div>
                <div class="app-footer-title">House Price Predictor</div>
                <div class="app-footer-sub">Built with a Random Forest model trained on real Zameen.com house listings.</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ----------------------------------------------------------------------
# Load model + data
# ----------------------------------------------------------------------
@st.cache_resource
def load_model():
    model = joblib.load("model.pkl")
    feature_cols = joblib.load("feature_cols.pkl")
    return model, feature_cols


@st.cache_data
def load_clean_data():
    try:
        return pd.read_csv("data/clean_data.csv")
    except FileNotFoundError:
        return None


@st.cache_data
def load_coordinates():
    try:
        return pd.read_csv("data/area_coordinates.csv")
    except FileNotFoundError:
        return None


# ----------------------------------------------------------------------
# Price / size parsing helpers (same logic as scraper.py)
# ----------------------------------------------------------------------
def parse_price(text):
    m = PRICE_RE.search(text)
    if not m:
        return None, None
    value = m.group(1).replace(",", "")
    unit = m.group(2)
    try:
        return float(value), unit
    except ValueError:
        return None, unit


def parse_size(text):
    m = SIZE_RE.search(text)
    if not m:
        return None, None
    return float(m.group(1)), m.group(2)


def price_to_pkr(value, unit):
    if value is None:
        return None
    unit = (unit or "").lower()
    if unit == "crore":
        return value * 1_00_00_000
    if unit in ("lakh", "lac"):
        return value * 1_00_000
    if unit == "arab":
        return value * 1_00_00_00_000
    return value


def size_to_marla(value, unit):
    if value is None:
        return None
    if (unit or "").lower() == "kanal":
        return value * 20
    return value


def format_price(price):
    if price >= 1_00_00_000:
        return f"PKR {price / 1_00_00_000:.2f} Crore"
    return f"PKR {price / 1_00_000:.2f} Lakh"


def scrape_zameen_listing(url):
    """Fetch a single Zameen.com listing page and extract its key details.

    Zameen listing pages show a clean summary near the top of the page
    (before the "Overview" section) with the price and "N Beds / N Baths /
    N Marla" — we restrict parsing to that region to avoid picking up
    unrelated mentions further down the page (e.g. footer links, EMI
    calculators, "Price Index" sections).
    """
    resp = requests.get(url, headers=HEADERS, timeout=20)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    all_lines = [l.strip() for l in soup.get_text("\n").split("\n") if l.strip()]

    try:
        overview_idx = all_lines.index("Overview")
    except ValueError:
        overview_idx = len(all_lines)
    header_lines = all_lines[:overview_idx]
    header_text = "\n".join(header_lines)

    data = {"Price_PKR": None, "Size_Marla": None, "Bedrooms": None, "Bathrooms": None, "Location": None}

    price_val, price_unit = parse_price(header_text)
    data["Price_PKR"] = price_to_pkr(price_val, price_unit)

    size_val, size_unit = parse_size(header_text)
    data["Size_Marla"] = size_to_marla(size_val, size_unit)

    beds_match = re.search(r"(\d+)\s*Beds?\b", header_text, re.IGNORECASE)
    if beds_match:
        data["Bedrooms"] = beds_match.group(1)

    baths_match = re.search(r"(\d+)\s*Baths?\b", header_text, re.IGNORECASE)
    if baths_match:
        data["Bathrooms"] = baths_match.group(1)

    for line in header_lines:
        if any(c.lower() in line.lower() for c in ALL_CITIES):
            data["Location"] = line
            break

    title_tag = soup.find("title")
    data["Title"] = title_tag.get_text(strip=True) if title_tag else url

    detected_city = None
    if data["Location"]:
        for c in ALL_CITIES:
            if c.lower() in data["Location"].lower():
                detected_city = c
                break
    data["City"] = detected_city

    return data
