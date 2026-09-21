"""
pages/3_Model_Performance.py — Model Performance
"""

import os

import pandas as pd
import streamlit as st

from utils import apply_page_config, render_footer, render_header

apply_page_config("Model Performance")

render_header()

st.markdown('<div class="section-title">Model Performance</div>', unsafe_allow_html=True)
st.caption("How well the model predicts prices, and what it learned matters most.")

# Quick stats
col1, col2, col3 = st.columns(3)
stats = [
    ("0.787", "R² Score (Random Forest)"),
    ("PKR 37.5 Lakh", "Mean Absolute Error"),
    ("5", "Cities in Training Data"),
]
for col, (value, label) in zip([col1, col2, col3], stats):
    with col:
        st.markdown(
            f'<div class="stat-card"><div class="stat-value">{value}</div><div class="stat-label">{label}</div></div>',
            unsafe_allow_html=True,
        )

st.write("")
st.markdown('<div class="section-title" style="margin-top:1rem;">Model Comparison</div>', unsafe_allow_html=True)

comparison_data = [
    ("Random Forest", 5_869_221, 3_749_191, 0.787),
    ("Random Forest (Tuned)", 5_881_184, 3_771_301, 0.786),
    ("Linear Regression", 5_928_606, 3_966_297, 0.783),
    ("XGBoost", 5_939_537, 3_792_216, 0.782),
]

rows_html = ""
for i, (name, rmse, mae, r2) in enumerate(comparison_data):
    highlight = ' style="background-color:#FBF8FD;"' if i == 0 else ""
    rows_html += (
        f"<tr{highlight}>"
        f'<td style="padding:10px 14px; font-weight:600; color:#3E2A5E;">{name}</td>'
        f'<td style="padding:10px 14px; text-align:right; color:#5A4B70;">{rmse:,}</td>'
        f'<td style="padding:10px 14px; text-align:right; color:#5A4B70;">{mae:,}</td>'
        f'<td style="padding:10px 14px; text-align:right; font-weight:600; color:#B8912C;">{r2:.3f}</td>'
        "</tr>"
    )

st.markdown(
    f"""
    <div class="section-card" style="padding:0; overflow:hidden;">
    <table style="width:100%; border-collapse:collapse; font-size:13px; font-family:'Inter',sans-serif;">
        <thead>
            <tr style="background-color:#3E2A5E;">
                <th style="padding:12px 14px; text-align:left; color:#F5F1E8; font-weight:600;">Model</th>
                <th style="padding:12px 14px; text-align:right; color:#F5F1E8; font-weight:600;">RMSE (PKR)</th>
                <th style="padding:12px 14px; text-align:right; color:#F5F1E8; font-weight:600;">MAE (PKR)</th>
                <th style="padding:12px 14px; text-align:right; color:#F5F1E8; font-weight:600;">R² Score</th>
            </tr>
        </thead>
        <tbody>
            {rows_html}
        </tbody>
    </table>
    </div>
    """,
    unsafe_allow_html=True,
)
st.caption("Random Forest was selected as the final model — highest R², lowest RMSE.")

st.markdown('<div class="section-title" style="margin-top:1.5rem;">Feature Importance</div>', unsafe_allow_html=True)
feature_importance_path = "notebooks/feature_importance.png"
if os.path.exists(feature_importance_path):
    st.image(feature_importance_path, use_container_width=True)
    st.caption("Size is by far the strongest predictor of price, followed by bathrooms, bedrooms, and city.")
else:
    st.info("Run `model_training.ipynb` to generate this chart.")

st.markdown('<div class="section-title" style="margin-top:1.5rem;">Predicted vs Actual Price</div>', unsafe_allow_html=True)
pred_vs_actual_path = "notebooks/predicted_vs_actual.png"
if os.path.exists(pred_vs_actual_path):
    st.image(pred_vs_actual_path, use_container_width=True)
    st.caption(
        "Points near the red line are accurate predictions. The model is most reliable for mid-range houses, "
        "and less reliable for very cheap or very expensive properties."
    )
else:
    st.info("Run `model_training.ipynb` to generate this chart.")

st.markdown('<div class="section-title" style="margin-top:1.5rem;">Known Limitations</div>', unsafe_allow_html=True)
st.markdown(
    """
    <div class="section-card">
        <ul style="font-size:13px; color:#5A4B70; line-height:1.7; margin:0; padding-left:1.1rem;">
            <li>Very small houses (under 5 Marla) are rare in the training data and are priced inconsistently
                even for similar specs — predictions for these are less reliable.</li>
            <li>The model only covers Houses (not Flats/Plots), since Flats were too rare in these cities'
                listings to model reliably.</li>
            <li>Coverage is limited to 5 cities: Gujrat, Gujranwala, Sialkot, Jhelum, and Wazirabad.</li>
        </ul>
    </div>
    """,
    unsafe_allow_html=True,
)

st.write("")
render_footer()
