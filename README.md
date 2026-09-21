# 🏠 House Price Predictor — Gujrat, Gujranwala, Sialkot, Jhelum & Wazirabad

An end-to-end machine learning project that predicts house prices in five Punjab
(Pakistan) cities, built entirely on real listings scraped from
[Zameen.com](https://www.zameen.com).

**Live demo:** https://house-price-predictor-rapflznjocectfhm7d74ms.streamlit.app/

---

## Problem Statement

Real estate pricing in mid-size Pakistani cities is opaque — there's no easy way
for a buyer or seller to check whether a listed price is fair. This project scrapes
real listings, trains a model on them, and wraps it in a dashboard that:

- Predicts a fair price for a house given its size, bedrooms, bathrooms, and city
- Checks whether a **real Zameen.com listing** is overpriced, underpriced, or fair
- Visualizes the underlying market data (price trends, correlations, location maps)

## Dataset

- **Source:** Zameen.com (scraped directly — see `scraper.py` and `detail_scraper.py`)
- **Coverage:** Gujrat, Gujranwala, Sialkot, Jhelum, Wazirabad
- **Size:** ~1,500 raw listings → ~1,225 after cleaning
- **Fields:** Price, Size (Marla), Bedrooms, Bathrooms, City, exact Location

**Note:** Flats/Apartments were scraped but were too rare in these cities'
listings (fewer than 30 out of ~1,500) to model reliably, so this project
focuses on **Houses** only.

## Tech Stack

| Layer | Tools |
|---|---|
| Scraping | Python, Requests, BeautifulSoup |
| Data | Pandas, NumPy |
| Modeling | Scikit-learn, XGBoost |
| Dashboard | Streamlit, Folium, Geopy |
| Notebooks | Jupyter |

## Methodology

1. **Scraping** (`scraper.py`, `scrape_new_cities.py`) — Listing pages scraped
   across all 5 cities. `detail_scraper.py` then visits each individual listing
   page to extract Bedrooms, Bathrooms, and exact location.
2. **Cleaning** (`notebooks/data_cleaning.ipynb`) — Duplicates, missing values,
   and statistical outliers (IQR method) removed.
3. **EDA** (`notebooks/eda_analysis.ipynb`) — Price distributions, correlations,
   and city-level comparisons.
4. **Modeling** (`notebooks/baseline_model.ipynb`, `notebooks/model_training.ipynb`) —
   Linear Regression, Random Forest, and XGBoost trained and compared.
5. **Dashboard** (`app.py` + `pages/`) — Multi-page Streamlit app: price
   prediction, a "Deal Checker" for real listings, market insights, and model
   performance transparency.

## Model Performance

| Model | RMSE (PKR) | MAE (PKR) | R² Score |
|---|---|---|---|
| **Random Forest** | 5,869,221 | 3,749,191 | **0.787** |
| Random Forest (Tuned) | 5,881,184 | 3,771,301 | 0.786 |
| Linear Regression | 5,928,606 | 3,966,297 | 0.783 |
| XGBoost | 5,939,537 | 3,792,216 | 0.782 |

**Selected model:** Random Forest — highest R², lowest RMSE.

### Known Limitations

- Very small houses (under 5 Marla) are rare in the training data and priced
  inconsistently even for similar specs — predictions here are less reliable.
- Coverage is limited to Houses in 5 cities; Flats and Plots are out of scope.

## Dashboard Features

- **Predict Price** — Input a city, size, bedrooms, and bathrooms to get an
  instant estimate, with similar listings and a map of matching houses.
- **Deal Checker** — Paste any Zameen.com listing URL; the app scrapes it live
  and tells you if it's a fair deal, overpriced, or underpriced.
- **Market Insights** — Price distributions, price-vs-size trends, and a
  feature correlation heatmap.
- **Model Performance** — Full model comparison table, feature importance, and
  a predicted-vs-actual accuracy plot.

## How to Run Locally

```bash
git clone https://github.com/<your-username>/<your-repo>.git
cd <your-repo>
pip install -r requirements.txt
streamlit run app.py
```

To regenerate the data pipeline from scratch:

```bash
python scraper.py              # scrape Gujrat, Gujranwala, Sialkot
python scrape_new_cities.py    # scrape Jhelum, Wazirabad
python detail_scraper.py       # get Bedrooms/Bathrooms/Location per listing
python geocode_areas.py        # geocode areas for the map feature
# then run notebooks/data_cleaning.ipynb, model_training.ipynb in order
```

## Project Structure

```
real-estate-price-prediction/
├── data/
│   ├── raw_data.csv
│   ├── raw_data_detailed.csv
│   ├── clean_data.csv
│   └── area_coordinates.csv
├── notebooks/
│   ├── data_cleaning.ipynb
│   ├── eda_analysis.ipynb
│   ├── baseline_model.ipynb
│   └── model_training.ipynb
├── pages/
│   ├── 1_🔎_Deal_Checker.py
│   ├── 2_📊_Market_Insights.py
│   ├── 3_🤖_Model_Performance.py
│   └── 4_ℹ️_About.py
├── scraper.py
├── scrape_new_cities.py
├── detail_scraper.py
├── geocode_areas.py
├── utils.py
├── app.py
├── model.pkl
├── feature_cols.pkl
├── requirements.txt
└── README.md
```

## Future Improvements

- Extract features from listing titles (e.g. "corner", "furnished", "brand new").
- Add more cities to increase training data size and diversity.
- Use k-fold cross-validation for a more robust accuracy estimate.
- Extend the Deal Checker to Flats and Plots.

---

Built as an end-to-end ML portfolio project — scraping → cleaning → modeling → deployment.
