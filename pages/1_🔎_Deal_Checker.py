"""
pages/1_Deal_Checker.py — Deal Checker
"""

import pandas as pd
import requests
import streamlit as st

from utils import apply_page_config, format_price, load_model, render_footer, render_header, scrape_zameen_listing

apply_page_config("Deal Checker")

model, feature_cols = load_model()

render_header()

st.markdown(
    """
    <div style="font-size:13px; color:#374B41; margin-bottom:1rem; line-height:1.5;">
    Paste a Zameen.com listing URL (for a house in Gujrat, Gujranwala, Sialkot, Jhelum, or Wazirabad).
    We'll fetch its details live and tell you if it's a fair deal, overpriced, or underpriced —
    based on what our model expects for similar houses.
    </div>
    """,
    unsafe_allow_html=True,
)

st.session_state.setdefault("deal_input_key", 0)

listing_url = st.text_input(
    "Zameen listing URL",
    placeholder="https://www.zameen.com/Property/...",
    label_visibility="collapsed",
    key=f"deal_url_{st.session_state['deal_input_key']}",
)
check_clicked = st.button("🔍  Check This Listing", key="deal_btn")

if check_clicked:
    if not listing_url or "zameen.com" not in listing_url:
        st.error("Please paste a valid Zameen.com listing URL.")
    else:
        with st.spinner("Fetching listing details..."):
            try:
                listing = scrape_zameen_listing(listing_url)
            except requests.exceptions.RequestException as e:
                listing = None
                st.error(f"Couldn't fetch this listing: {e}")

        if listing is not None:
            missing = [
                k for k in ["Price_PKR", "Size_Marla", "Bedrooms", "Bathrooms", "City"]
                if listing.get(k) is None
            ]
            if missing:
                st.warning(
                    f"Couldn't extract all needed details from this listing (missing: {', '.join(missing)}). "
                    "This may be a Plot, Commercial listing, or a page format we don't support — "
                    "the Deal Checker currently only works for Houses in our 5 supported cities."
                )
            else:
                try:
                    bedrooms_val = float(listing["Bedrooms"])
                    bathrooms_val = float(listing["Bathrooms"])
                except ValueError:
                    bedrooms_val = None
                    bathrooms_val = None

                if bedrooms_val is None:
                    st.warning("Couldn't parse bedroom/bathroom numbers from this listing.")
                else:
                    row = {col: 0 for col in feature_cols}
                    if "Size_Marla" in row:
                        row["Size_Marla"] = listing["Size_Marla"]
                    if "Bedrooms" in row:
                        row["Bedrooms"] = bedrooms_val
                    if "Bathrooms" in row:
                        row["Bathrooms"] = bathrooms_val
                    city_col = f"City_{listing['City']}"
                    if city_col in row:
                        row[city_col] = 1

                    X_input = pd.DataFrame([row])[feature_cols]
                    fair_price = model.predict(X_input)[0]
                    actual_price = listing["Price_PKR"]
                    diff_pct = (actual_price - fair_price) / fair_price * 100

                    if diff_pct > 12:
                        verdict, css_class = "⚠️ Overpriced", "verdict-bad"
                    elif diff_pct < -12:
                        verdict, css_class = "✅ Good Deal (Underpriced)", "verdict-good"
                    else:
                        verdict, css_class = "👍 Fair Price", "verdict-fair"

                    st.markdown(f'<span class="verdict-badge {css_class}">{verdict}</span>', unsafe_allow_html=True)

                    st.markdown(
                        f"""
                        <div class="result-card">
                            <div class="result-label">{listing['Title']}</div>
                            <div style="font-size:13px; color:#6B7A70; margin-bottom:12px;">
                                {listing['Size_Marla']:g} Marla · {bedrooms_val:.0f} Bed · {bathrooms_val:.0f} Bath · {listing['City']}
                            </div>
                            <div style="display:flex; gap:2.5rem;">
                                <div>
                                    <div style="font-size:11px; color:#9CA3AF;">LISTED PRICE</div>
                                    <div style="font-family:'Sora',sans-serif; font-size:24px; font-weight:700; color:#3E2A5E;">{format_price(actual_price)}</div>
                                </div>
                                <div>
                                    <div style="font-size:11px; color:#9CA3AF;">MODEL'S FAIR ESTIMATE</div>
                                    <div style="font-family:'Sora',sans-serif; font-size:24px; font-weight:700; color:#B8912C;">{format_price(fair_price)}</div>
                                </div>
                            </div>
                            <div class="result-raw" style="margin-top:10px;">
                                Difference: {diff_pct:+.1f}% vs. model's estimate
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                    st.caption(
                        "This is a model-based estimate, not professional appraisal — use it as a starting "
                        "reference point alongside your own research."
                    )

                    st.write("")
                    if st.button("🔄  Check Another Listing", key="reset_deal", type="secondary"):
                        st.session_state["deal_input_key"] += 1
                        st.rerun()

st.write("")
render_footer()
