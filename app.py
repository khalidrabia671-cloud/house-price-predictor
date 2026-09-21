"""
app.py — Predict Price (Home page)
------------------------------------
Streamlit multi-page dashboard entry point.
Run locally:
    streamlit run app.py
"""

import folium
import pandas as pd
import streamlit as st
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium

from utils import (
    ALL_CITIES,
    apply_page_config,
    format_price,
    load_clean_data,
    load_coordinates,
    load_model,
    render_footer,
    render_header,
)

apply_page_config("House Price Predictor")

model, feature_cols = load_model()
df = load_clean_data()
coords_df = load_coordinates()

render_header()

st.session_state.setdefault("predict_form_key", 0)
fk = st.session_state["predict_form_key"]

col1, col2 = st.columns(2)
with col1:
    st.markdown('<div class="input-label">CITY</div>', unsafe_allow_html=True)
    city = st.selectbox("City", ALL_CITIES, label_visibility="collapsed", key=f"city_{fk}")
with col2:
    st.markdown('<div class="input-label">SIZE (MARLA)</div>', unsafe_allow_html=True)
    size_marla = st.number_input("Size", min_value=1.0, max_value=50.0, value=5.0, step=0.5, label_visibility="collapsed", key=f"size_{fk}")

col3, col4 = st.columns(2)
with col3:
    st.markdown('<div class="input-label">BEDROOMS</div>', unsafe_allow_html=True)
    bedrooms = st.number_input("Bedrooms", min_value=1, max_value=15, value=3, step=1, label_visibility="collapsed", key=f"beds_{fk}")
with col4:
    st.markdown('<div class="input-label">BATHROOMS</div>', unsafe_allow_html=True)
    bathrooms = st.number_input("Bathrooms", min_value=1, max_value=15, value=3, step=1, label_visibility="collapsed", key=f"baths_{fk}")

st.write("")
predict_clicked = st.button("🧮  Predict Price", key="predict_btn")

if predict_clicked:
    st.session_state["show_result"] = True
    st.session_state["inputs"] = {
        "city": city,
        "size_marla": size_marla,
        "bedrooms": bedrooms,
        "bathrooms": bathrooms,
    }

if st.session_state.get("show_result"):
    saved = st.session_state["inputs"]
    city = saved["city"]
    size_marla = saved["size_marla"]
    bedrooms = saved["bedrooms"]
    bathrooms = saved["bathrooms"]

    row = {col: 0 for col in feature_cols}
    if "Size_Marla" in row:
        row["Size_Marla"] = size_marla
    if "Bedrooms" in row:
        row["Bedrooms"] = bedrooms
    if "Bathrooms" in row:
        row["Bathrooms"] = bathrooms
    city_col = f"City_{city}"
    if city_col in row:
        row[city_col] = 1

    X_input = pd.DataFrame([row])[feature_cols]
    predicted_price = model.predict(X_input)[0]

    if predicted_price >= 1_00_00_000:
        crore = predicted_price / 1_00_00_000
        display_price = f'PKR {crore:.2f} <span class="gold">Crore</span>'
    else:
        lakh = predicted_price / 1_00_000
        display_price = f'PKR {lakh:.2f} <span class="gold">Lakh</span>'

    st.markdown(
        f"""
        <div class="result-card">
            <div class="result-label">Estimated price — {size_marla:g} Marla, {city}</div>
            <div class="result-price">{display_price}</div>
            <div class="result-raw">Raw value: PKR {predicted_price:,.0f}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if df is not None:
        size_low, size_high = df["Size_Marla"].quantile([0.05, 0.95])
        typical_beds_for_size = df[
            (df["Size_Marla"] >= size_marla - 1) & (df["Size_Marla"] <= size_marla + 1)
        ]["Bedrooms"]

        warns = []
        if size_marla < size_low or size_marla > size_high:
            warns.append(
                f"Listings of this size ({size_marla:g} Marla) are rare in the training data "
                f"(typical range: {size_low:.1f}–{size_high:.1f} Marla) — this prediction may be less reliable."
            )
        if not typical_beds_for_size.empty and (
            bedrooms < typical_beds_for_size.min() or bedrooms > typical_beds_for_size.max()
        ):
            warns.append(
                f"Houses of this size usually have {typical_beds_for_size.min():.0f}-{typical_beds_for_size.max():.0f} bedrooms — "
                f"{bedrooms} bedrooms is an uncommon combination in the training data."
            )
        if warns:
            st.warning("⚠️ " + " ".join(warns))

    if df is not None:
        candidates = df[df["City"] == city].copy()
        candidates["distance"] = (
            (candidates["Size_Marla"] - size_marla).abs() * 2
            + (candidates["Bedrooms"] - bedrooms).abs()
            + (candidates["Bathrooms"] - bathrooms).abs()
        )
        similar = candidates.sort_values("distance").head(3)

        rows_html = ""
        if similar.empty:
            rows_html = '<div style="font-size:13px; color:#9CA3AF;">No similar listings found for this city.</div>'
        else:
            for _, r in similar.iterrows():
                price_str = format_price(r["Price_PKR"])
                rows_html += (
                    '<div class="listing-row">'
                    f'<span><i class="ti ti-home" style="color:#9CA3AF; margin-right:6px;"></i>'
                    f"{r['Size_Marla']:g} Marla · {r['Bedrooms']:.0f} Bed · {r['Bathrooms']:.0f} Bath</span>"
                    f'<span class="listing-price">{price_str}</span>'
                    "</div>"
                )

        st.markdown(
            f'<div class="section-card"><div class="section-title">Similar Listings</div>{rows_html}</div>',
            unsafe_allow_html=True,
        )

        st.markdown('<div class="section-title" style="margin-top:1.5rem;">Matching Houses on Map</div>', unsafe_allow_html=True)

        if coords_df is None:
            st.caption("Map data not available yet — run `python geocode_areas.py` first to enable this.")
        else:
            map_candidates = df[
                (df["City"] == city)
                & (df["Bedrooms"] == bedrooms)
                & (df["Size_Marla"].between(size_marla - 1.5, size_marla + 1.5))
            ].copy()

            map_candidates = map_candidates.merge(coords_df, on=["Area", "City"], how="left")
            map_candidates = map_candidates.dropna(subset=["Latitude", "Longitude"])

            if map_candidates.empty:
                st.caption("No matching listings with known locations found for this search.")
            else:
                center_lat = map_candidates["Latitude"].mean()
                center_lon = map_candidates["Longitude"].mean()

                fmap = folium.Map(location=[center_lat, center_lon], zoom_start=12, tiles="OpenStreetMap")
                marker_cluster = MarkerCluster().add_to(fmap)

                for _, r in map_candidates.iterrows():
                    price_str = format_price(r["Price_PKR"])
                    popup_html = (
                        f"<b>{r['Area']}</b><br>"
                        f"{r['Size_Marla']:g} Marla · {r['Bedrooms']:.0f} Bed · {r['Bathrooms']:.0f} Bath<br>"
                        f"<b style='color:#B8912C;'>{price_str}</b>"
                    )
                    folium.Marker(
                        location=[r["Latitude"], r["Longitude"]],
                        popup=folium.Popup(popup_html, max_width=220),
                        icon=folium.Icon(color="darkgreen", icon="home", prefix="fa"),
                    ).add_to(marker_cluster)

                st.caption(f"{len(map_candidates)} matching houses found — click a marker for details.")
                st_folium(fmap, width=None, height=420, key="predict_map")

    st.write("")
    reset_col1, reset_col2 = st.columns([1, 3])
    with reset_col1:
        if st.button("🔄  New Search", key="reset_predict", type="secondary"):
            st.session_state["show_result"] = False
            st.session_state["predict_form_key"] += 1
            st.rerun()
else:
    st.markdown(
        """
        <div class="empty-state">
            <div class="emoji">🏡</div>
            <div class="msg">Fill in the property details above and click <b>Predict Price</b><br>to get an instant, data-driven estimate.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.write("")
render_footer()
