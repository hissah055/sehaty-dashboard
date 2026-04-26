import base64
import time
from pathlib import Path

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="Sehhaty Smart Feedback Dashboard",
    layout="wide"
)

# =========================
# Green Progress Bar Style
# =========================
st.markdown(
    """
    <style>
    .stProgress > div > div > div > div {
        background-color: #22C55E !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# =========================
# Fixed Plot Style
# =========================
PLOT_TEMPLATE = "plotly_white"
PLOT_FONT_COLOR = "#FFFFFF"
PLOT_BG_COLOR = "#0C848F"
PLOT_AXIS_TITLE_SIZE = 20
PLOT_TICK_SIZE = 15
PLOT_TITLE_SIZE = 24


# =========================
# Logo Function
# =========================
def get_logo_html():
    logo_path = Path("sehhaty_logo.png")

    if logo_path.exists():
        logo_base64 = base64.b64encode(logo_path.read_bytes()).decode()
        return (
            f'<img src="data:image/png;base64,{logo_base64}" '
            f'style="width:300px; height:170px; object-fit:contain; margin-right:45px;">'
        )

    return '<div style="font-size:60px; margin-right:20px;">📊</div>'


# =========================
# Header Design
# =========================
logo_html = get_logo_html()

header_html = f"""
<div style="padding:28px 30px; border-radius:22px; background:linear-gradient(135deg, #0891B2, #0F766E); color:white; margin-bottom:25px; box-shadow:0 10px 30px rgba(0,0,0,0.18); display:flex; align-items:center;">
{logo_html}
<div>
<h1 style="margin-bottom:8px; font-size:42px;">Sehhaty Smart Feedback Intelligence Platform</h1>
<p style="font-size:19px; margin:0;">An interactive dashboard for analyzing Sehhaty app reviews by sentiment, themes, subthemes, language, and rating.</p>
</div>
</div>
"""

st.markdown(header_html, unsafe_allow_html=True)

uploaded_file = st.file_uploader("📂 Upload Excel file", type=["xlsx"])


# =========================
# Cache Excel Loading
# =========================
@st.cache_data(show_spinner=False)
def load_excel(file):
    return pd.read_excel(file)


# =========================
# Cleaning Functions
# =========================
def clean_sentiment(value):
    value = str(value).strip().lower()

    if value in ["positive", "pos", "إيجابي", "ايجابي"]:
        return "Positive"
    elif value in ["negative", "neg", "سلبي"]:
        return "Negative"
    elif value in ["neutral", "neu", "محايد"]:
        return "Neutral"
    else:
        return "Unknown"


def clean_category(value):
    if pd.isna(value):
        return "Unknown"

    value = str(value).strip()

    if value == "" or value.lower() in ["nan", "none", "null", "undefined"]:
        return "Unknown"

    return value


def normalize_col_name(col):
    return (
        str(col)
        .strip()
        .lower()
        .replace(" ", "")
        .replace("_", "")
        .replace("-", "")
    )


def find_column_by_keywords(columns, keywords):
    for col in columns:
        col_clean = normalize_col_name(col)
        for keyword in keywords:
            if keyword in col_clean:
                return col
    return None


def remove_private_columns(dataframe):
    private_cols = []

    for col in dataframe.columns:
        col_clean = normalize_col_name(col)

        if (
            "username" in col_clean
            or col_clean in ["name", "reviewer", "author"]
            or "reviewer" in col_clean
            or "author" in col_clean
        ):
            private_cols.append(col)

    return dataframe.drop(columns=private_cols, errors="ignore")


def add_time_features(dataframe):
    df = dataframe.copy()

    year_col = find_column_by_keywords(
        df.columns,
        ["reviewyear", "year"]
    )

    month_col = find_column_by_keywords(
        df.columns,
        ["reviewmonth", "month"]
    )

    date_col = find_column_by_keywords(
        df.columns,
        ["reviewdate", "date"]
    )

    if year_col is not None:
        df["Dashboard_Year"] = pd.to_numeric(df[year_col], errors="coerce")
    elif date_col is not None:
        parsed_dates = pd.to_datetime(df[date_col], errors="coerce", dayfirst=True)
        df["Dashboard_Year"] = parsed_dates.dt.year
    else:
        df["Dashboard_Year"] = pd.NA

    if month_col is not None:
        df["Dashboard_Month"] = pd.to_numeric(df[month_col], errors="coerce")
    elif date_col is not None:
        parsed_dates = pd.to_datetime(df[date_col], errors="coerce", dayfirst=True)
        df["Dashboard_Month"] = parsed_dates.dt.month
    else:
        df["Dashboard_Month"] = pd.NA

    df["Dashboard_Quarter"] = pd.NA
    valid_months = df["Dashboard_Month"].notna()

    df.loc[valid_months, "Dashboard_Quarter"] = (
        "Q" + (((df.loc[valid_months, "Dashboard_Month"].astype(int) - 1) // 3) + 1).astype(str)
    )

    return df


def get_sorted_unique(series):
    values = series.dropna().unique().tolist()
    try:
        values = sorted(values)
    except Exception:
        values = sorted(values, key=lambda x: str(x))
    return values


def clear_dashboard_filters():
    filter_keys = [
        "filter_years",
        "filter_quarters",
        "filter_months",
        "filter_ratings",
        "filter_languages",
        "filter_sentiments",
        "filter_themes",
        "filter_subthemes",
        "analysis_ready",
        "last_filter_state",
    ]

    for key in filter_keys:
        if key in st.session_state:
            del st.session_state[key]


if uploaded_file:
    df = load_excel(uploaded_file)
    df = add_time_features(df)

    # =========================
    # Column Settings
    # =========================
    st.sidebar.header("⚙️ Column Settings")

    text_col = st.sidebar.selectbox(
        "Review text column",
        df.columns,
        index=list(df.columns).index("Content_Clean") if "Content_Clean" in df.columns else 0
    )

    sentiment_col = st.sidebar.selectbox(
        "Sentiment column",
        df.columns,
        index=list(df.columns).index("Sentiment") if "Sentiment" in df.columns else 0
    )

    theme_col = st.sidebar.selectbox(
        "Main Theme column",
        df.columns,
        index=list(df.columns).index("Theme") if "Theme" in df.columns else 0
    )

    subtheme_col = st.sidebar.selectbox(
        "Subtheme column",
        df.columns,
        index=list(df.columns).index("Subtheme") if "Subtheme" in df.columns else 0
    )

    language_col = st.sidebar.selectbox(
        "Language column",
        df.columns,
        index=list(df.columns).index("Language") if "Language" in df.columns else 0
    )

    rating_col = st.sidebar.selectbox(
        "Rating column",
        df.columns,
        index=list(df.columns).index("Rating") if "Rating" in df.columns else 0
    )

    # =========================
    # Prepare Filter Data
    # =========================
    filter_df = df.copy()
    filter_df[text_col] = filter_df[text_col].fillna("").astype(str)
    filter_df[theme_col] = filter_df[theme_col].apply(clean_category)
    filter_df[subtheme_col] = filter_df[subtheme_col].apply(clean_category)
    filter_df[language_col] = filter_df[language_col].apply(clean_category)
    filter_df[rating_col] = pd.to_numeric(filter_df[rating_col], errors="coerce")
    filter_df["Sentiment_Clean"] = filter_df[sentiment_col].apply(clean_sentiment)

    # =========================
    # Dashboard Filter Style
    # =========================
    filter_style_html = """
<style>
.filter-title {
    background: linear-gradient(135deg, #0891B2, #0F766E);
    color: white;
    padding: 12px 18px;
    border-radius: 16px;
    font-size: 22px;
    font-weight: 800;
    margin-top: 10px;
    margin-bottom: 16px;
    box-shadow: 0 6px 18px rgba(0,0,0,0.18);
}

label p {
    font-weight: 800 !important;
    color: #F8FAFC !important;
}

/* صندوق الفلتر الحقيقي */
div[data-baseweb="select"] > div {
    background: linear-gradient(145deg, rgba(255,255,255,0.10), rgba(255,255,255,0.04)) !important;
    border: 1px solid rgba(255,255,255,0.22) !important;
    border-radius: 16px !important;
    color: white !important;
    min-height: 52px !important;
    box-shadow:
        inset 0 0 8px rgba(255,255,255,0.06),
        0 8px 22px rgba(0,0,0,0.16) !important;
}

/* النص داخل الفلاتر */
div[data-baseweb="select"] * {
    color: #FFFFFF !important;
}

/* السهم الداخلي فضي كريستال */
div[data-baseweb="select"] svg {
    fill: #E5E7EB !important;
    color: #E5E7EB !important;
    filter: drop-shadow(0 0 4px rgba(255,255,255,0.55));
}

/* تغيير لون الخيارات المختارة بدل الأحمر */
div[data-baseweb="tag"] {
    background: linear-gradient(135deg, #0F766E, #0C848F) !important;
    border: 1px solid rgba(255,255,255,0.35) !important;
    border-radius: 10px !important;
    color: white !important;
    box-shadow: 0 0 10px rgba(255,255,255,0.15) !important;
}

div[data-baseweb="tag"] span {
    color: white !important;
    font-weight: 700 !important;
}

div[data-baseweb="tag"] svg {
    fill: #E5E7EB !important;
    color: #E5E7EB !important;
}
</style>
<div class="filter-title">🔎 Dashboard Filters</div>
"""
    st.markdown(filter_style_html, unsafe_allow_html=True)

    # =========================
    # Filter Options
    # =========================
    year_options = get_sorted_unique(filter_df["Dashboard_Year"])
    year_options = [int(y) for y in year_options if pd.notna(y)]

    quarter_order = ["Q1", "Q2", "Q3", "Q4"]
    quarter_options = [
        q for q in quarter_order
        if q in filter_df["Dashboard_Quarter"].dropna().unique().tolist()
    ]

    month_options = get_sorted_unique(filter_df["Dashboard_Month"])
    month_options = [int(m) for m in month_options if pd.notna(m)]

    rating_options = get_sorted_unique(filter_df[rating_col])
    rating_options = [
        int(r) if float(r).is_integer() else r
        for r in rating_options
        if pd.notna(r)
    ]

    language_options = get_sorted_unique(filter_df[language_col])

    sentiment_options = ["Positive", "Negative", "Neutral"]
    sentiment_options = [
        s for s in sentiment_options
        if s in filter_df["Sentiment_Clean"].dropna().unique().tolist()
    ]

    THEME_ORDER = [
        "Technical Performance",
        "Content & Services",
        "User Experience & Sentiment",
        "Suggestions & UI Design",
        "Security & Support"
    ]

    SUBTHEME_ORDER = [
        "App Speed",
        "Loading Time",
        "Crashes/Freezes",
        "Errors/Bugs",
        "Connectivity/Network",
        "Stability",
        "General",
        "General_Technical",

        "Appointment Booking",
        "Results Delivery",
        "Reports/Documents",
        "Prescriptions",
        "Records/Vaccination",
        "Teleconsultation",
        "General_Content",

        "Ease of Use",
        "Navigation",
        "UI Clarity",
        "Onboarding",
        "Overall Satisfaction",
        "Accessibility Help & Guidance",
        "General_UX",

        "Feature Request – Dark Mode",
        "Notifications & Reminders",
        "Layout Improvements",
        "Customization",
        "Language Options",
        "Accessibility Enhancements",
        "General_Suggestions",

        "Login/OTP",
        "Password Reset",
        "Account Verification",
        "Privacy/Permissions",
        "Support Responsiveness",
        "Account Access Issues",
        "General_Security"
    ]

    existing_themes = filter_df[theme_col].dropna().unique().tolist()
    existing_subthemes = filter_df[subtheme_col].dropna().unique().tolist()

    theme_options = [x for x in THEME_ORDER if x in existing_themes]
    extra_themes = [x for x in get_sorted_unique(filter_df[theme_col]) if x not in theme_options and x != "Unknown"]
    theme_options = theme_options + extra_themes

    subtheme_options = [x for x in SUBTHEME_ORDER if x in existing_subthemes]
    extra_subthemes = [x for x in get_sorted_unique(filter_df[subtheme_col]) if x not in subtheme_options and x != "Unknown"]
    subtheme_options = subtheme_options + extra_subthemes

    # =========================
    # Top Filters
    # =========================
    f1, f2, f3, f4 = st.columns(4)

    with f1:
        selected_years = st.multiselect(
            "Review Year",
            options=year_options,
            default=[],
            placeholder="All years",
            key="filter_years"
        )

    with f2:
        selected_quarters = st.multiselect(
            "Quarter",
            options=quarter_options,
            default=[],
            placeholder="All quarters",
            key="filter_quarters"
        )

    with f3:
        selected_months = st.multiselect(
            "Month",
            options=month_options,
            default=[],
            placeholder="All months",
            key="filter_months"
        )

    with f4:
        selected_ratings = st.multiselect(
            "Rating",
            options=rating_options,
            default=[],
            placeholder="All ratings",
            key="filter_ratings"
        )

    f5, f6, f7, f8 = st.columns([1.2, 1.2, 1.6, 1.6])

    with f5:
        selected_languages = st.multiselect(
            "Language",
            options=language_options,
            default=[],
            placeholder="All languages",
            key="filter_languages"
        )

    with f6:
        selected_sentiments = st.multiselect(
            "Sentiment",
            options=sentiment_options,
            default=[],
            placeholder="All sentiments",
            key="filter_sentiments"
        )

    with f7:
        selected_themes = st.multiselect(
            "Theme",
            options=theme_options,
            default=[],
            placeholder="All themes",
            key="filter_themes"
        )

    with f8:
        selected_subthemes = st.multiselect(
            "Subtheme",
            options=subtheme_options,
            default=[],
            placeholder="All subthemes",
            key="filter_subthemes"
        )

    clear_col, info_col = st.columns([1, 5])

    with clear_col:
        if st.button("🧹 Clear all filters", use_container_width=True):
            clear_dashboard_filters()
            st.rerun()

    with info_col:
        st.caption("No selection means All. Choose the filters, then click Run Analysis to display the dashboard.")

    # =========================
    # Run Analysis Control
    # =========================
    current_filter_state = (
        tuple(selected_years),
        tuple(selected_quarters),
        tuple(selected_months),
        tuple(selected_ratings),
        tuple(selected_languages),
        tuple(selected_sentiments),
        tuple(selected_themes),
        tuple(selected_subthemes),
    )

    if "last_filter_state" not in st.session_state:
        st.session_state["last_filter_state"] = current_filter_state

    if st.session_state["last_filter_state"] != current_filter_state:
        st.session_state["analysis_ready"] = False
        st.session_state["last_filter_state"] = current_filter_state

    run_col, note_col = st.columns([1.2, 4.8])

    with run_col:
        run_analysis = st.button("🚀 Run Analysis", type="primary", use_container_width=True)

    with note_col:
        st.caption("The charts and results will appear after clicking Run Analysis.")

    if run_analysis:
        progress_bar = st.progress(0, text="Preparing data...")

        progress_bar.progress(25, text="Applying selected filters...")
        time.sleep(0.25)

        progress_bar.progress(55, text="Calculating indicators...")
        time.sleep(0.25)

        progress_bar.progress(80, text="Building charts...")
        time.sleep(0.25)

        progress_bar.progress(100, text="Analysis completed!")
        time.sleep(0.25)

        st.session_state["analysis_ready"] = True
        progress_bar.empty()

    if not st.session_state.get("analysis_ready", False):
        st.info("👆 Please choose the filters, then click **Run Analysis** to display the dashboard charts and results.")
        st.stop()

    def apply_dashboard_filters(dataframe):
        result = dataframe.copy()

        if selected_years and "Dashboard_Year" in result.columns:
            result = result[result["Dashboard_Year"].isin(selected_years)]

        if selected_quarters and "Dashboard_Quarter" in result.columns:
            result = result[result["Dashboard_Quarter"].isin(selected_quarters)]

        if selected_months and "Dashboard_Month" in result.columns:
            result = result[result["Dashboard_Month"].isin(selected_months)]

        if selected_ratings:
            result = result[result[rating_col].isin(selected_ratings)]

        if selected_languages:
            result = result[result[language_col].isin(selected_languages)]

        if selected_sentiments:
            result = result[result["Sentiment_Clean"].isin(selected_sentiments)]

        if selected_themes:
            result = result[result[theme_col].isin(selected_themes)]

        if selected_subthemes:
            result = result[result[subtheme_col].isin(selected_subthemes)]

        return result

    analysis_source_df = apply_dashboard_filters(filter_df)

    analysis_df = analysis_source_df[
        (analysis_source_df["Sentiment_Clean"] != "Unknown") &
        (analysis_source_df[theme_col] != "Unknown") &
        (analysis_source_df[subtheme_col] != "Unknown")
    ].copy()

    if analysis_df.empty:
        st.warning("⚠️ No data available for the selected filters. Please adjust the filters.")
        st.stop()

    # =========================
    # Data Preview at the Top
    # =========================
    st.markdown("---")
    st.subheader("🔍 Data Preview")
    st.caption("Showing a filtered preview with usernames removed for privacy.")

    preview_df = analysis_source_df.head(5).copy()
    preview_df = remove_private_columns(preview_df)
    preview_df.insert(0, "Review_ID", range(1, len(preview_df) + 1))
    preview_df = preview_df.reset_index(drop=True)

    st.dataframe(preview_df, width="stretch", hide_index=True)

    st.success("✅ Analysis Completed!")

    total_reviews = len(analysis_source_df)
    avg_rating = analysis_df[rating_col].mean()
    positive_count = (analysis_df["Sentiment_Clean"] == "Positive").sum()
    negative_count = (analysis_df["Sentiment_Clean"] == "Negative").sum()
    neutral_count = (analysis_df["Sentiment_Clean"] == "Neutral").sum()

    st.caption(
        f"Filtered dataset: {len(analysis_source_df):,} reviews | "
        f"Valid analysis rows: {len(analysis_df):,}"
    )

    # =========================
    # KPI Metric Cards
    # =========================
    metric_cards_html = f"""
<style>
.metric-grid {{
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 16px;
    margin-top: 14px;
    margin-bottom: 10px;
}}
.metric-card {{
    background: linear-gradient(135deg, #0F766E, #0C848F);
    border-radius: 18px;
    padding: 20px 18px;
    color: white;
    box-shadow: 0 8px 24px rgba(0,0,0,0.20);
    border: 1px solid rgba(255,255,255,0.14);
    transition: transform 0.25s ease, box-shadow 0.25s ease;
    min-height: 120px;
}}
.metric-card:hover {{
    transform: translateY(-4px);
    box-shadow: 0 14px 28px rgba(0,0,0,0.28);
}}
.metric-label {{
    font-size: 16px;
    font-weight: 700;
    opacity: 0.95;
    margin-bottom: 10px;
}}
.metric-value {{
    font-size: 30px;
    font-weight: 850;
    line-height: 1.2;
}}
.metric-icon {{
    font-size: 24px;
    margin-right: 8px;
}}
@media (max-width: 1100px) {{
    .metric-grid {{
        grid-template-columns: repeat(2, 1fr);
    }}
}}
@media (max-width: 700px) {{
    .metric-grid {{
        grid-template-columns: repeat(1, 1fr);
    }}
}}
</style>
<div class="metric-grid"><div class="metric-card"><div class="metric-label"><span class="metric-icon">📝</span>Total Reviews</div><div class="metric-value">{total_reviews:,}</div></div><div class="metric-card"><div class="metric-label"><span class="metric-icon">⭐</span>Avg Rating</div><div class="metric-value">{avg_rating:.2f}</div></div><div class="metric-card"><div class="metric-label"><span class="metric-icon">😊</span>Positive</div><div class="metric-value">{positive_count:,}</div></div><div class="metric-card"><div class="metric-label"><span class="metric-icon">😟</span>Negative</div><div class="metric-value">{negative_count:,}</div></div><div class="metric-card"><div class="metric-label"><span class="metric-icon">😐</span>Neutral</div><div class="metric-value">{neutral_count:,}</div></div></div>
"""
    st.markdown(metric_cards_html, unsafe_allow_html=True)

    # =========================
    # Smart Insights Summary
    # =========================
    st.markdown("---")
    st.subheader("✨ Smart Insights Summary")

    top_year_text = "N/A"
    best_year_text = "N/A"
    top_theme_text = "N/A"
    negative_theme_text = "N/A"
    top_subtheme_text = "N/A"
    negative_rate_text = "0%"

    year_insight_df = analysis_df.dropna(subset=["Dashboard_Year"]).copy()
    if not year_insight_df.empty:
        year_counts = year_insight_df.groupby("Dashboard_Year").size()
        top_year = int(year_counts.idxmax())
        top_year_count = int(year_counts.max())
        top_year_text = f"{top_year} ({top_year_count:,})"

    year_rating_insight_df = analysis_df.dropna(subset=["Dashboard_Year", rating_col]).copy()
    if not year_rating_insight_df.empty:
        avg_by_year = year_rating_insight_df.groupby("Dashboard_Year")[rating_col].mean()
        best_year = int(avg_by_year.idxmax())
        best_year_rating = avg_by_year.max()
        best_year_text = f"{best_year} ({best_year_rating:.2f})"

    theme_counts = analysis_df[theme_col].value_counts()
    if not theme_counts.empty:
        top_theme_text = f"{theme_counts.index[0]} ({theme_counts.iloc[0]:,})"

    negative_df = analysis_df[analysis_df["Sentiment_Clean"] == "Negative"]
    if not negative_df.empty:
        negative_theme_counts = negative_df[theme_col].value_counts()
        if not negative_theme_counts.empty:
            negative_theme_text = f"{negative_theme_counts.index[0]} ({negative_theme_counts.iloc[0]:,})"

    subtheme_counts = analysis_df[subtheme_col].value_counts()
    if not subtheme_counts.empty:
        top_subtheme_text = f"{subtheme_counts.index[0]} ({subtheme_counts.iloc[0]:,})"

    if len(analysis_df) > 0:
        negative_rate = (negative_count / len(analysis_df)) * 100
        negative_rate_text = f"{negative_rate:.1f}%"

    insights_html = f"""
<style>
.insight-grid {{
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 18px;
    margin-top: 18px;
    margin-bottom: 18px;
}}
.insight-card {{
    background: linear-gradient(135deg, #0F766E, #0C848F);
    padding: 22px 24px;
    border-radius: 20px;
    color: white;
    box-shadow: 0 10px 28px rgba(0,0,0,0.22);
    border: 1px solid rgba(255,255,255,0.22);
    transition: transform 0.25s ease, box-shadow 0.25s ease, border 0.25s ease;
    min-height: 145px;
    overflow-wrap: anywhere;
}}
.insight-card:hover {{
    transform: translateY(-7px) scale(1.015);
    box-shadow: 0 16px 36px rgba(0,0,0,0.32);
    border: 1px solid rgba(255,255,255,0.45);
}}
.insight-icon {{
    font-size: 34px;
    margin-bottom: 10px;
    display: block;
}}
.insight-title {{
    font-size: 15px;
    font-weight: 700;
    opacity: 0.9;
    margin-bottom: 8px;
}}
.insight-value {{
    font-size: 23px;
    font-weight: 850;
    line-height: 1.25;
}}
@media (max-width: 900px) {{
    .insight-grid {{
        grid-template-columns: repeat(1, 1fr);
    }}
}}
</style>
<div class="insight-grid"><div class="insight-card"><span class="insight-icon">📅</span><div class="insight-title">Most Active Year</div><div class="insight-value">{top_year_text}</div></div><div class="insight-card"><span class="insight-icon">⭐</span><div class="insight-title">Best Avg Rating Year</div><div class="insight-value">{best_year_text}</div></div><div class="insight-card"><span class="insight-icon">🏆</span><div class="insight-title">Top Theme</div><div class="insight-value">{top_theme_text}</div></div><div class="insight-card"><span class="insight-icon">🔥</span><div class="insight-title">Most Negative Theme</div><div class="insight-value">{negative_theme_text}</div></div><div class="insight-card"><span class="insight-icon">🧩</span><div class="insight-title">Top Subtheme</div><div class="insight-value">{top_subtheme_text}</div></div><div class="insight-card"><span class="insight-icon">📉</span><div class="insight-title">Negative Reviews Rate</div><div class="insight-value">{negative_rate_text}</div></div></div>
"""
    st.markdown(insights_html, unsafe_allow_html=True)

    st.markdown("---")

    # =========================
    # Time Analysis: Year + Quarter
    # =========================
    st.subheader("📅 Time-Based Analysis")

    time_col1, time_col2 = st.columns(2)

    with time_col1:
        year_df = analysis_df.dropna(subset=["Dashboard_Year"]).copy()

        if not year_df.empty:
            year_summary = year_df.groupby("Dashboard_Year").agg(
                Total_Reviews=("Dashboard_Year", "count")
            ).reset_index()

            year_summary["Dashboard_Year"] = year_summary["Dashboard_Year"].astype(int)
            year_summary = year_summary.sort_values("Dashboard_Year")
            year_summary["Year_Label"] = year_summary["Dashboard_Year"].astype(str)

            fig_year = px.bar(
                year_summary,
                x="Year_Label",
                y="Total_Reviews",
                text=year_summary["Total_Reviews"].apply(lambda x: f"{x:,}"),
                title="Total Reviews by Year"
            )

            fig_year.update_traces(
                marker_color="#25B6C8",
                textposition="outside",
                textfont=dict(color=PLOT_FONT_COLOR, size=13),
                cliponaxis=False
            )

            fig_year.update_layout(
                template=PLOT_TEMPLATE,
                height=450,
                font=dict(color=PLOT_FONT_COLOR),
                title=dict(
                    text="Total Reviews by Year",
                    font=dict(size=22, color=PLOT_FONT_COLOR)
                ),
                xaxis=dict(
                    title=dict(
                        text="Year",
                        font=dict(size=PLOT_AXIS_TITLE_SIZE, color=PLOT_FONT_COLOR)
                    ),
                    type="category",
                    categoryorder="array",
                    categoryarray=year_summary["Year_Label"].tolist(),
                    showgrid=False,
                    tickfont=dict(size=PLOT_TICK_SIZE, color=PLOT_FONT_COLOR)
                ),
                yaxis=dict(
                    title=dict(
                        text="Total Reviews",
                        font=dict(size=PLOT_AXIS_TITLE_SIZE, color=PLOT_FONT_COLOR)
                    ),
                    showgrid=False,
                    tickfont=dict(size=PLOT_TICK_SIZE, color=PLOT_FONT_COLOR)
                ),
                plot_bgcolor=PLOT_BG_COLOR,
                paper_bgcolor=PLOT_BG_COLOR,
                showlegend=False
            )

            st.plotly_chart(fig_year, width="stretch")

    with time_col2:
        year_rating_df = analysis_df.dropna(subset=["Dashboard_Year", rating_col]).copy()

        if not year_rating_df.empty:
            avg_year_summary = year_rating_df.groupby("Dashboard_Year").agg(
                Avg_Rating=(rating_col, "mean")
            ).reset_index()

            avg_year_summary["Dashboard_Year"] = avg_year_summary["Dashboard_Year"].astype(int)
            avg_year_summary = avg_year_summary.sort_values("Dashboard_Year")
            avg_year_summary["Year_Label"] = avg_year_summary["Dashboard_Year"].astype(str)

            fig_avg_year = go.Figure()

            fig_avg_year.add_trace(go.Scatter(
                x=avg_year_summary["Year_Label"],
                y=avg_year_summary["Avg_Rating"],
                mode="lines+markers+text",
                line=dict(color="#FF8A00", width=4),
                marker=dict(size=11, color="#FF8A00"),
                text=[f"{v:.2f}" for v in avg_year_summary["Avg_Rating"]],
                textposition="top center",
                textfont=dict(color=PLOT_FONT_COLOR, size=13),
                name="Avg Rating"
            ))

            fig_avg_year.update_layout(
                template=PLOT_TEMPLATE,
                height=450,
                title=dict(
                    text="Avg Rating by Year",
                    font=dict(size=22, color=PLOT_FONT_COLOR)
                ),
                font=dict(color=PLOT_FONT_COLOR),
                xaxis=dict(
                    title=dict(
                        text="Year",
                        font=dict(size=PLOT_AXIS_TITLE_SIZE, color=PLOT_FONT_COLOR)
                    ),
                    type="category",
                    categoryorder="array",
                    categoryarray=avg_year_summary["Year_Label"].tolist(),
                    showgrid=False,
                    tickfont=dict(size=PLOT_TICK_SIZE, color=PLOT_FONT_COLOR)
                ),
                yaxis=dict(
                    title=dict(
                        text="Avg Rating",
                        font=dict(size=PLOT_AXIS_TITLE_SIZE, color=PLOT_FONT_COLOR)
                    ),
                    range=[0, 5.3],
                    showgrid=False,
                    tickfont=dict(size=PLOT_TICK_SIZE, color=PLOT_FONT_COLOR)
                ),
                plot_bgcolor=PLOT_BG_COLOR,
                paper_bgcolor=PLOT_BG_COLOR,
                showlegend=False
            )

            st.plotly_chart(fig_avg_year, width="stretch")

    quarter_col1, quarter_col2 = st.columns(2)

    with quarter_col1:
        quarter_df = analysis_df.dropna(subset=["Dashboard_Quarter"]).copy()

        if not quarter_df.empty:
            quarter_summary = quarter_df.groupby("Dashboard_Quarter").agg(
                Total_Reviews=("Dashboard_Quarter", "count")
            ).reset_index()

            quarter_summary["Quarter_Order"] = quarter_summary["Dashboard_Quarter"].map(
                {"Q1": 1, "Q2": 2, "Q3": 3, "Q4": 4}
            )

            quarter_summary = quarter_summary.sort_values("Quarter_Order")

            fig_quarter = px.bar(
                quarter_summary,
                x="Dashboard_Quarter",
                y="Total_Reviews",
                text=quarter_summary["Total_Reviews"].apply(lambda x: f"{x:,}"),
                title="Total Reviews by Quarter"
            )

            fig_quarter.update_traces(
                marker_color="#25B6C8",
                textposition="outside",
                textfont=dict(color=PLOT_FONT_COLOR, size=13),
                cliponaxis=False
            )

            fig_quarter.update_layout(
                template=PLOT_TEMPLATE,
                height=450,
                title=dict(
                    text="Total Reviews by Quarter",
                    font=dict(size=22, color=PLOT_FONT_COLOR)
                ),
                font=dict(color=PLOT_FONT_COLOR),
                xaxis=dict(
                    title=dict(
                        text="Quarter",
                        font=dict(size=PLOT_AXIS_TITLE_SIZE, color=PLOT_FONT_COLOR)
                    ),
                    showgrid=False,
                    tickfont=dict(size=PLOT_TICK_SIZE, color=PLOT_FONT_COLOR)
                ),
                yaxis=dict(
                    title=dict(
                        text="Total Reviews",
                        font=dict(size=PLOT_AXIS_TITLE_SIZE, color=PLOT_FONT_COLOR)
                    ),
                    showgrid=False,
                    tickfont=dict(size=PLOT_TICK_SIZE, color=PLOT_FONT_COLOR)
                ),
                plot_bgcolor=PLOT_BG_COLOR,
                paper_bgcolor=PLOT_BG_COLOR,
                showlegend=False
            )

            st.plotly_chart(fig_quarter, width="stretch")

    with quarter_col2:
        rating_dist = analysis_df.dropna(subset=[rating_col]).copy()

        if not rating_dist.empty:
            rating_summary = rating_dist.groupby(rating_col).size().reset_index(name="Total_Reviews")
            rating_summary = rating_summary.sort_values(rating_col)

            fig_rating = px.bar(
                rating_summary,
                x=rating_col,
                y="Total_Reviews",
                text=rating_summary["Total_Reviews"].apply(lambda x: f"{x:,}"),
                title="Total Reviews by Rating"
            )

            fig_rating.update_traces(
                marker_color="#25B6C8",
                textposition="outside",
                textfont=dict(color=PLOT_FONT_COLOR, size=13),
                cliponaxis=False
            )

            fig_rating.update_layout(
                template=PLOT_TEMPLATE,
                height=450,
                title=dict(
                    text="Total Reviews by Rating",
                    font=dict(size=22, color=PLOT_FONT_COLOR)
                ),
                font=dict(color=PLOT_FONT_COLOR),
                xaxis=dict(
                    title=dict(
                        text="Rating",
                        font=dict(size=PLOT_AXIS_TITLE_SIZE, color=PLOT_FONT_COLOR)
                    ),
                    showgrid=False,
                    tickfont=dict(size=PLOT_TICK_SIZE, color=PLOT_FONT_COLOR)
                ),
                yaxis=dict(
                    title=dict(
                        text="Total Reviews",
                        font=dict(size=PLOT_AXIS_TITLE_SIZE, color=PLOT_FONT_COLOR)
                    ),
                    showgrid=False,
                    tickfont=dict(size=PLOT_TICK_SIZE, color=PLOT_FONT_COLOR)
                ),
                plot_bgcolor=PLOT_BG_COLOR,
                paper_bgcolor=PLOT_BG_COLOR,
                showlegend=False
            )

            st.plotly_chart(fig_rating, width="stretch")

    st.markdown("---")

    # =========================
    # Reviews & Avg Rating by Theme
    # =========================
    st.subheader("📊 Reviews & Avg Rating by Theme")

    theme_summary = analysis_df.groupby(theme_col).agg(
        Total_Reviews=(theme_col, "count"),
        Avg_Rating=(rating_col, "mean")
    ).reset_index()

    theme_summary = theme_summary.sort_values(by="Total_Reviews", ascending=False)

    fig_theme = go.Figure()

    fig_theme.add_trace(go.Bar(
        x=theme_summary[theme_col].astype(str),
        y=theme_summary["Total_Reviews"],
        name="Total Reviews",
        marker_color="#25B6C8",
        text=theme_summary["Total_Reviews"],
        texttemplate="%{text:,}",
        textposition="outside",
        textfont=dict(size=12, color=PLOT_FONT_COLOR),
        cliponaxis=False,
        hovertemplate="<b>%{x}</b><br>Total Reviews: %{y:,}<extra></extra>"
    ))

    fig_theme.add_trace(go.Scatter(
        x=theme_summary[theme_col].astype(str),
        y=theme_summary["Avg_Rating"],
        name="Avg Rating",
        mode="lines+markers+text",
        yaxis="y2",
        line=dict(color="#FF8A00", width=4),
        marker=dict(size=11, color="#FF8A00"),
        text=[f"{v:.2f}" for v in theme_summary["Avg_Rating"]],
        textposition=["bottom center"] + ["top center"] * (len(theme_summary) - 1),
        textfont=dict(color=PLOT_FONT_COLOR, size=14),
        hovertemplate="<b>%{x}</b><br>Avg Rating: %{y:.2f}<extra></extra>"
    ))

    fig_theme.update_layout(
        template=PLOT_TEMPLATE,
        height=590,
        title=dict(
            text="Reviews & Avg Rating by Theme",
            font=dict(size=PLOT_TITLE_SIZE, color=PLOT_FONT_COLOR)
        ),
        font=dict(color=PLOT_FONT_COLOR),
        showlegend=True,
        legend=dict(
            orientation="h",
            y=1.08,
            x=0.38,
            font=dict(size=15, color=PLOT_FONT_COLOR),
            title=dict(font=dict(color=PLOT_FONT_COLOR))
        ),
        xaxis=dict(
            title=dict(
                text="Theme",
                font=dict(size=PLOT_AXIS_TITLE_SIZE, color=PLOT_FONT_COLOR)
            ),
            tickangle=-25,
            showgrid=False,
            tickfont=dict(size=PLOT_TICK_SIZE, color=PLOT_FONT_COLOR)
        ),
        yaxis=dict(
            title=dict(
                text="Total Reviews",
                font=dict(size=PLOT_AXIS_TITLE_SIZE, color=PLOT_FONT_COLOR)
            ),
            type="linear",
            showgrid=False,
            zeroline=False,
            tickfont=dict(size=PLOT_TICK_SIZE, color=PLOT_FONT_COLOR)
        ),
        yaxis2=dict(
            title=dict(
                text="Avg Rating",
                font=dict(size=PLOT_AXIS_TITLE_SIZE, color=PLOT_FONT_COLOR)
            ),
            overlaying="y",
            side="right",
            range=[0, 5.3],
            showgrid=False,
            zeroline=False,
            tickfont=dict(size=PLOT_TICK_SIZE, color=PLOT_FONT_COLOR)
        ),
        plot_bgcolor=PLOT_BG_COLOR,
        paper_bgcolor=PLOT_BG_COLOR,
        margin=dict(t=105, b=125, l=80, r=80)
    )

    st.plotly_chart(fig_theme, width="stretch")

    st.markdown("---")

    # =========================
    # Sentiment & Language
    # =========================
    colA, colB = st.columns(2)

    with colA:
        st.subheader("😊 Sentiment Distribution")

        sentiment_data = analysis_df["Sentiment_Clean"].value_counts().reset_index()
        sentiment_data.columns = ["Sentiment", "Count"]

        fig_sent = px.bar(
            sentiment_data,
            x="Sentiment",
            y="Count",
            color="Sentiment",
            text=sentiment_data["Count"].apply(lambda x: f"{x:,}"),
            color_discrete_map={
                "Positive": "#10B981",
                "Negative": "#EF4444",
                "Neutral": "#3B82F6"
            }
        )

        fig_sent.update_traces(
            textposition="outside",
            textfont=dict(size=14, color=PLOT_FONT_COLOR),
            cliponaxis=False
        )

        fig_sent.update_layout(
            template=PLOT_TEMPLATE,
            height=480,
            bargap=0.3,
            title=dict(
                text="Sentiment Distribution",
                font=dict(size=22, color=PLOT_FONT_COLOR)
            ),
            font=dict(color=PLOT_FONT_COLOR),
            legend=dict(
                title=dict(
                    text="Sentiment",
                    font=dict(size=14, color=PLOT_FONT_COLOR)
                ),
                font=dict(size=14, color=PLOT_FONT_COLOR)
            ),
            xaxis=dict(
                title=dict(
                    text="Sentiment",
                    font=dict(size=PLOT_AXIS_TITLE_SIZE, color=PLOT_FONT_COLOR)
                ),
                showgrid=False,
                tickfont=dict(size=PLOT_TICK_SIZE, color=PLOT_FONT_COLOR)
            ),
            yaxis=dict(
                title=dict(
                    text="Count",
                    font=dict(size=PLOT_AXIS_TITLE_SIZE, color=PLOT_FONT_COLOR)
                ),
                showgrid=False,
                tickfont=dict(size=PLOT_TICK_SIZE, color=PLOT_FONT_COLOR)
            ),
            plot_bgcolor=PLOT_BG_COLOR,
            paper_bgcolor=PLOT_BG_COLOR
        )

        st.plotly_chart(fig_sent, width="stretch")

    with colB:
        st.subheader("🌐 Language Distribution")

        lang_data = analysis_df[language_col].value_counts().reset_index()
        lang_data.columns = ["Language", "Count"]

        fig_lang = px.pie(
            lang_data,
            names="Language",
            values="Count",
            hole=0.5,
            color="Language"
        )

        fig_lang.update_traces(
            textinfo="percent+label",
            textfont=dict(size=15, color=PLOT_FONT_COLOR)
        )

        fig_lang.update_layout(
            template=PLOT_TEMPLATE,
            height=480,
            title=dict(
                text="Language Distribution",
                font=dict(size=22, color=PLOT_FONT_COLOR)
            ),
            font=dict(color=PLOT_FONT_COLOR),
            legend=dict(
                title=dict(font=dict(color=PLOT_FONT_COLOR)),
                font=dict(size=15, color=PLOT_FONT_COLOR)
            ),
            plot_bgcolor=PLOT_BG_COLOR,
            paper_bgcolor=PLOT_BG_COLOR,
            showlegend=True
        )

        st.plotly_chart(fig_lang, width="stretch")

    st.markdown("---")

    # =========================
    # Negative Reviews by Theme
    # =========================
    st.subheader("🔥 Negative Reviews by Theme")

    neg_df = analysis_df[analysis_df["Sentiment_Clean"] == "Negative"]

    neg_theme = neg_df.groupby(theme_col).size().reset_index(name="Negative Reviews")
    neg_theme = neg_theme.sort_values(by="Negative Reviews", ascending=False)

    total_neg = len(neg_df)

    if total_neg > 0:
        neg_theme["Label"] = neg_theme["Negative Reviews"].apply(
            lambda x: f"{x:,} ({x / total_neg:.1%})"
        )
    else:
        neg_theme["Label"] = "0"

    colors = ["#7F1D1D"] + ["#DC2626"] * (len(neg_theme) - 1)

    fig_neg = go.Figure()

    fig_neg.add_trace(go.Bar(
        x=neg_theme["Negative Reviews"],
        y=neg_theme[theme_col],
        orientation="h",
        name="Negative Reviews",
        marker=dict(color=colors),
        text=neg_theme["Label"],
        textposition="outside",
        textfont=dict(size=14, color=PLOT_FONT_COLOR),
        cliponaxis=False,
        hovertemplate="<b>%{y}</b><br>Negative Reviews: %{x:,}<extra></extra>"
    ))

    max_neg = neg_theme["Negative Reviews"].max() if len(neg_theme) > 0 else 1

    fig_neg.update_layout(
        template=PLOT_TEMPLATE,
        height=530,
        title=dict(
            text="Negative Reviews by Theme",
            font=dict(size=22, color=PLOT_FONT_COLOR)
        ),
        font=dict(color=PLOT_FONT_COLOR),
        xaxis=dict(
            title=dict(
                text="Negative Reviews",
                font=dict(size=PLOT_AXIS_TITLE_SIZE, color=PLOT_FONT_COLOR)
            ),
            showgrid=False,
            range=[0, max_neg * 1.18],
            tickfont=dict(size=PLOT_TICK_SIZE, color=PLOT_FONT_COLOR)
        ),
        yaxis=dict(
            title=dict(
                text="Theme",
                font=dict(size=PLOT_AXIS_TITLE_SIZE, color=PLOT_FONT_COLOR)
            ),
            categoryorder="total ascending",
            showgrid=False,
            tickfont=dict(size=PLOT_TICK_SIZE, color=PLOT_FONT_COLOR)
        ),
        plot_bgcolor=PLOT_BG_COLOR,
        paper_bgcolor=PLOT_BG_COLOR,
        margin=dict(l=100, r=160, t=70, b=50),
        showlegend=False
    )

    st.plotly_chart(fig_neg, width="stretch")

    st.markdown("---")

    # =========================
    # Top Subthemes
    # =========================
    st.subheader("🧩 Top Subthemes")

    sub_data = analysis_df[subtheme_col].value_counts().head(20).reset_index()
    sub_data.columns = ["Subtheme", "Count"]

    fig_sub = px.bar(
        sub_data,
        x="Count",
        y="Subtheme",
        orientation="h",
        text=sub_data["Count"].apply(lambda x: f"{x:,}"),
        color="Count",
        color_continuous_scale="Teal"
    )

    fig_sub.update_traces(
        textposition="outside",
        textfont=dict(size=14, color=PLOT_FONT_COLOR),
        cliponaxis=False
    )

    max_sub = sub_data["Count"].max() if len(sub_data) > 0 else 1

    fig_sub.update_layout(
        template=PLOT_TEMPLATE,
        height=670,
        title=dict(
            text="Top Subthemes",
            font=dict(size=22, color=PLOT_FONT_COLOR)
        ),
        font=dict(color=PLOT_FONT_COLOR),
        xaxis=dict(
            title=dict(
                text="Count",
                font=dict(size=PLOT_AXIS_TITLE_SIZE, color=PLOT_FONT_COLOR)
            ),
            showgrid=False,
            range=[0, max_sub * 1.18],
            tickfont=dict(size=PLOT_TICK_SIZE, color=PLOT_FONT_COLOR)
        ),
        yaxis=dict(
            title=dict(
                text="Subtheme",
                font=dict(size=PLOT_AXIS_TITLE_SIZE, color=PLOT_FONT_COLOR)
            ),
            showgrid=False,
            categoryorder="total ascending",
            tickfont=dict(size=PLOT_TICK_SIZE, color=PLOT_FONT_COLOR)
        ),
        coloraxis_colorbar=dict(
            title=dict(
                text="Count",
                font=dict(color=PLOT_FONT_COLOR)
            ),
            tickfont=dict(color=PLOT_FONT_COLOR)
        ),
        plot_bgcolor=PLOT_BG_COLOR,
        paper_bgcolor=PLOT_BG_COLOR,
        margin=dict(l=100, r=170, t=70, b=50)
    )

    st.plotly_chart(fig_sub, width="stretch")

    st.markdown("---")

    # =========================
    # Full Filtered Data
    # =========================
    st.subheader("📄 Filtered Reviews Data")
    st.caption("Showing all filtered and anonymized rows so you can read the reviews based on the selected filters.")

    full_filtered_df = analysis_source_df.copy()
    full_filtered_df = remove_private_columns(full_filtered_df)
    full_filtered_df.insert(0, "Review_ID", range(1, len(full_filtered_df) + 1))
    full_filtered_df = full_filtered_df.reset_index(drop=True)

    st.dataframe(full_filtered_df, width="stretch", hide_index=True)
