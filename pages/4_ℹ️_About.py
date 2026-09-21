"""
pages/4_About.py — About / Methodology
"""

import streamlit as st

from utils import apply_page_config, render_footer, render_header

apply_page_config("About")

render_header()

st.markdown('<div class="section-title">About This Project</div>', unsafe_allow_html=True)

st.markdown(
    """
    <div class="section-card">
        <p style="font-size:14px; color:#374B41; line-height:1.7;">
        This tool estimates house prices in five Punjab cities — Gujrat, Gujranwala, Sialkot, Jhelum,
        and Wazirabad — using real listings scraped from Zameen.com. It was built as an end-to-end
        machine learning project: web scraping, data cleaning, exploratory analysis, model training,
        and this interactive dashboard.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="section-title" style="margin-top:1.5rem;">Methodology</div>', unsafe_allow_html=True)
st.markdown(
    """
    <div class="section-card">
        <ol style="font-size:13px; color:#374B41; line-height:1.9; margin:0; padding-left:1.1rem;">
            <li><b>Scraping</b> — Listing pages for Houses and Flats were scraped across all 5 cities
                (~1,500 listings). Individual listing pages were then visited to extract Bedrooms,
                Bathrooms, and exact location.</li>
            <li><b>Cleaning</b> — Duplicates, missing values, and statistical outliers (IQR method) were
                removed. Listings without Bedroom/Bathroom data (mostly Plots) were dropped, narrowing
                the scope to Houses.</li>
            <li><b>Modeling</b> — Linear Regression, Random Forest, and XGBoost were trained and compared.
                Random Forest (with hyperparameter tuning) performed best.</li>
            <li><b>Dashboard</b> — This Streamlit app lets you predict a price, check whether a real
                listing is a fair deal, and explore the underlying market data.</li>
        </ol>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="section-title" style="margin-top:1.5rem;">Tech Stack</div>', unsafe_allow_html=True)
st.markdown(
    """
    <div class="section-card">
        <div style="font-size:13px; color:#374B41; line-height:1.8;">
        <b>Scraping:</b> Python, Requests, BeautifulSoup<br>
        <b>Data:</b> Pandas, NumPy<br>
        <b>Modeling:</b> Scikit-learn, XGBoost<br>
        <b>Dashboard:</b> Streamlit, Folium, Geopy<br>
        <b>Notebooks:</b> Jupyter (cleaning, EDA, model training)
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="section-title" style="margin-top:1.5rem;">Future Improvements</div>', unsafe_allow_html=True)
st.markdown(
    """
    <div class="section-card">
        <ul style="font-size:13px; color:#374B41; line-height:1.8; margin:0; padding-left:1.1rem;">
            <li>Extract additional features from listing titles (e.g. "corner", "furnished", "new").</li>
            <li>Add more cities to increase training data size and diversity.</li>
            <li>Use cross-validation for a more robust accuracy estimate.</li>
            <li>Extend the Deal Checker to Flats and Plots.</li>
        </ul>
    </div>
    """,
    unsafe_allow_html=True,
)

st.write("")
render_footer()
