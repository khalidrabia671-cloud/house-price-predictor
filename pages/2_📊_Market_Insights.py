"""
pages/2_Market_Insights.py — Market Insights (EDA)
"""

import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

from utils import apply_page_config, load_clean_data, render_footer, render_header

apply_page_config("Market Insights")

df = load_clean_data()

render_header()

st.markdown('<div class="section-title">Market Insights</div>', unsafe_allow_html=True)
st.caption("Exploratory analysis of the cleaned Zameen.com listings dataset.")

if df is None:
    st.warning("No data found — run the data pipeline (scraper → cleaning) first.")
else:
    # Quick stats row
    col1, col2, col3, col4 = st.columns(4)
    stats = [
        (f"{len(df):,}", "Total Listings"),
        (f"{df['City'].nunique()}", "Cities Covered"),
        (f"PKR {df['Price_PKR'].mean() / 1e7:.2f} Cr", "Average Price"),
        (f"{df['Size_Marla'].median():.1f}", "Median Size (Marla)"),
    ]
    for col, (value, label) in zip([col1, col2, col3, col4], stats):
        with col:
            st.markdown(
                f'<div class="stat-card"><div class="stat-value">{value}</div><div class="stat-label">{label}</div></div>',
                unsafe_allow_html=True,
            )

    st.write("")

    tab1, tab2, tab3, tab4 = st.tabs(
        ["Price by City", "Price Distribution", "Price vs Size", "Correlation"]
    )

    with tab1:
        avg_price = df.groupby("City", observed=True)["Price_PKR"].mean().sort_values() / 1e7
        st.bar_chart(avg_price, x_label="City", y_label="Average Price (Crore PKR)", color="#3E2A5E")
        st.caption("Average listed price by city, in Crore PKR.")

    with tab2:
        hist_data = (df["Price_PKR"] / 1e7).round(1)
        st.bar_chart(
            hist_data.value_counts().sort_index(),
            x_label="Price (Crore PKR)",
            y_label="Number of Listings",
            color="#D4AF37",
        )
        st.caption("Most listings cluster in the affordable-to-mid range, with a long tail of expensive outliers.")

    with tab3:
        scatter_df = df[["Size_Marla", "Price_PKR"]].copy()
        scatter_df["Price_Crore"] = scatter_df["Price_PKR"] / 1e7
        st.scatter_chart(scatter_df, x="Size_Marla", y="Price_Crore", x_label="Size (Marla)", y_label="Price (Crore PKR)", color="#3E2A5E")
        st.caption("Larger houses generally cost more, though the relationship isn't perfectly linear.")

    with tab4:
        numeric_cols = ["Price_PKR", "Size_Marla", "Bedrooms", "Bathrooms"]
        corr = df[numeric_cols].corr()

        fig, ax = plt.subplots(figsize=(5, 4))
        fig.patch.set_facecolor("#F3ECF7")
        sns.heatmap(corr, annot=False, cmap="Purples", ax=ax, cbar=False, vmin=0, vmax=1)
        for i in range(len(corr)):
            for j in range(len(corr)):
                value = corr.iloc[i, j]
                text_color = "#FFFFFF" if value > 0.72 else "#3E2A5E"
                ax.text(j + 0.5, i + 0.5, f"{value:.2f}", ha="center", va="center",
                         color=text_color, fontsize=11, fontweight="bold")
        ax.set_title("Feature Correlation", color="#3E2A5E")
        st.pyplot(fig)
        st.caption("How strongly each feature relates to price and to each other.")

st.write("")
render_footer()
