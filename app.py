import base64
import time
from pathlib import Path
from io import BytesIO



import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go



st.set_page_config(
    page_title="Sehhaty Smart Feedback Dashboard",
    layout="wide"
)



# =========================
# App Global Style - Better Visibility in Light & Dark Mode
# =========================
st.markdown(
    """
    <style>
    :root {
        --accent-main: #0891B2;
        --accent-dark: #0F766E;
        --label-color: #22D3EE;
        --helper-color: #D1D9E6;
        --text-dark: #111827;
        --placeholder-color: #64748B;
        --box-border: #CBD5E1;
        --hover-bg: #E0F2FE;
        --selected-bg: #CCFBF1;
        --menu-bg: #FFFFFF;
    }



    /* Green progress bar */
    .stProgress > div > div > div > div {
        background-color: #22C55E !important;
    }



    /* Main labels */
    label p,
    [data-testid="stWidgetLabel"] p,
    [data-testid="stWidgetLabel"] span {
        font-weight: 800 !important;
        color: var(--label-color) !important;
    }



    /* Sidebar labels + sidebar header */
    section[data-testid="stSidebar"] label p,
    section[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p,
    section[data-testid="stSidebar"] [data-testid="stWidgetLabel"] span,
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {
        color: var(--label-color) !important;
        font-weight: 800 !important;
    }



    /* File uploader label */
    [data-testid="stFileUploader"] label,
    [data-testid="stFileUploader"] label p,
    [data-testid="stFileUploader"] span {
        color: var(--label-color) !important;
        font-weight: 800 !important;
    }



    /* Captions / helper text */
    .stCaption,
    [data-testid="stCaptionContainer"],
    [data-testid="stCaptionContainer"] p,
    small {
        color: var(--helper-color) !important;
        font-weight: 650 !important;
    }



    /* Main select boxes + sidebar select boxes */
    div[data-baseweb="select"] > div,
    section[data-testid="stSidebar"] div[data-baseweb="select"] > div {
        background: #FFFFFF !important;
        border: 1px solid var(--box-border) !important;
        border-radius: 16px !important;
        color: var(--text-dark) !important;
        min-height: 52px !important;
        box-shadow: 0 8px 22px rgba(15, 23, 42, 0.10) !important;
    }



    div[data-baseweb="select"] *,
    section[data-testid="stSidebar"] div[data-baseweb="select"] * {
        color: var(--text-dark) !important;
    }



    div[data-baseweb="select"] svg,
    section[data-testid="stSidebar"] div[data-baseweb="select"] svg {
        fill: var(--accent-dark) !important;
        color: var(--accent-dark) !important;
        filter: drop-shadow(0 0 3px rgba(15,118,110,0.25));
    }



    /* ========================= */
    /* Force selected multiselect tags to teal, not red */
    /* ========================= */



    div[data-baseweb="tag"],
    span[data-baseweb="tag"],
    [data-baseweb="tag"],
    div[data-testid="stMultiSelect"] [data-baseweb="tag"],
    div[data-testid="stMultiSelect"] span[data-baseweb="tag"],
    .stMultiSelect [data-baseweb="tag"] {
        position: relative !important;
        overflow: hidden !important;
        background: linear-gradient(135deg, #0891B2 0%, #0F766E 100%) !important;
        background-color: #0F766E !important;
        border: 1px solid rgba(255,255,255,0.35) !important;
        border-radius: 13px !important;
        color: #FFFFFF !important;
        box-shadow:
            0 6px 14px rgba(15,118,110,0.28),
            inset 0 0 10px rgba(255,255,255,0.10) !important;
        padding: 5px 9px !important;
        transform: translateY(0);
        transition: all 0.25s ease !important;
    }



    div[data-baseweb="tag"] *,
    span[data-baseweb="tag"] *,
    [data-baseweb="tag"] *,
    div[data-testid="stMultiSelect"] [data-baseweb="tag"] *,
    .stMultiSelect [data-baseweb="tag"] * {
        background-color: transparent !important;
        color: #FFFFFF !important;
        fill: #FFFFFF !important;
    }



    div[data-baseweb="tag"] span,
    span[data-baseweb="tag"] span,
    [data-baseweb="tag"] span {
        color: #FFFFFF !important;
        font-weight: 800 !important;
        position: relative !important;
        z-index: 2 !important;
    }



    div[data-baseweb="tag"] svg,
    span[data-baseweb="tag"] svg,
    [data-baseweb="tag"] svg {
        fill: #FFFFFF !important;
        color: #FFFFFF !important;
        opacity: 0.95 !important;
        position: relative !important;
        z-index: 3 !important;
    }



    div[data-baseweb="tag"] button,
    span[data-baseweb="tag"] button,
    [data-baseweb="tag"] button {
        background: rgba(255,255,255,0.18) !important;
        border-radius: 50% !important;
        margin-left: 6px !important;
        transition: all 0.2s ease !important;
        position: relative !important;
        z-index: 3 !important;
    }



    div[data-baseweb="tag"] button:hover,
    span[data-baseweb="tag"] button:hover,
    [data-baseweb="tag"] button:hover {
        background: rgba(255,255,255,0.32) !important;
        transform: scale(1.05);
    }



    div[data-baseweb="tag"]::before,
    span[data-baseweb="tag"]::before,
    [data-baseweb="tag"]::before {
        content: "";
        position: absolute;
        top: -60%;
        left: -85%;
        width: 55%;
        height: 220%;
        background: linear-gradient(
            120deg,
            rgba(255,255,255,0.00) 0%,
            rgba(255,255,255,0.18) 40%,
            rgba(255,255,255,0.55) 50%,
            rgba(255,255,255,0.14) 60%,
            rgba(255,255,255,0.00) 100%
        );
        transform: rotate(20deg);
        animation: selectedTagShine 3.8s infinite ease-in-out;
        pointer-events: none;
        z-index: 1;
    }



    @keyframes selectedTagShine {
        0% {
            left: -85%;
            opacity: 0.15;
        }
        45% {
            left: 120%;
            opacity: 0.85;
        }
        100% {
            left: 120%;
            opacity: 0;
        }
    }



    div[data-baseweb="tag"]:hover,
    span[data-baseweb="tag"]:hover,
    [data-baseweb="tag"]:hover {
        transform: translateY(-2px) !important;
        box-shadow:
            0 9px 18px rgba(15,118,110,0.35),
            inset 0 0 12px rgba(255,255,255,0.18) !important;
        filter: brightness(1.05);
    }



    .stMultiSelect [data-baseweb="tag"],
    .stMultiSelect [data-baseweb="tag"] *,
    [data-testid="stMultiSelect"] [data-baseweb="tag"],
    [data-testid="stMultiSelect"] [data-baseweb="tag"] * {
        background: linear-gradient(135deg, #0891B2 0%, #0F766E 100%) !important;
        background-color: #0F766E !important;
        color: #FFFFFF !important;
        fill: #FFFFFF !important;
    }



    /* Force dropdown menu white in dark mode */
    div[data-baseweb="popover"] {
        background: transparent !important;
        color: var(--text-dark) !important;
    }



    div[data-baseweb="popover"] > div,
    div[data-baseweb="popover"] > div > div,
    div[data-baseweb="popover"] > div > div > div,
    div[data-baseweb="popover"] div {
        background-color: var(--menu-bg) !important;
        color: var(--text-dark) !important;
    }



    div[role="listbox"],
    ul[role="listbox"],
    div[data-baseweb="menu"],
    div[data-baseweb="popover"] ul,
    div[data-baseweb="popover"] li {
        background-color: var(--menu-bg) !important;
        color: var(--text-dark) !important;
        border-radius: 12px !important;
    }



    div[role="option"],
    li[role="option"] {
        background-color: var(--menu-bg) !important;
        color: var(--text-dark) !important;
        font-weight: 600 !important;
    }



    div[role="option"] *,
    li[role="option"] * {
        color: var(--text-dark) !important;
        background-color: transparent !important;
    }



    div[role="option"]:hover,
    li[role="option"]:hover {
        background-color: var(--hover-bg) !important;
        color: var(--text-dark) !important;
    }



    div[role="option"]:hover *,
    li[role="option"]:hover * {
        color: var(--text-dark) !important;
    }



    div[aria-selected="true"],
    li[aria-selected="true"] {
        background-color: var(--selected-bg) !important;
        color: var(--text-dark) !important;
    }



    div[aria-selected="true"] *,
    li[aria-selected="true"] * {
        color: var(--text-dark) !important;
    }



    div[data-baseweb="popover"] input {
        background-color: #F8FAFC !important;
        color: var(--text-dark) !important;
        border: 1px solid var(--box-border) !important;
        border-radius: 10px !important;
        caret-color: var(--text-dark) !important;
    }



    div[data-baseweb="popover"] input::placeholder {
        color: var(--placeholder-color) !important;
        opacity: 1 !important;
    }



    div[data-baseweb="popover"] input[value],
    div[data-baseweb="popover"] label,
    div[data-baseweb="popover"] span,
    div[data-baseweb="popover"] p {
        color: var(--text-dark) !important;
    }



    div.stButton > button[kind="primary"] {
        background: linear-gradient(135deg, var(--accent-main), var(--accent-dark)) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        font-weight: 800 !important;
        box-shadow: 0 8px 20px rgba(15, 118, 110, 0.25) !important;
    }



    div.stButton > button[kind="primary"]:hover {
        filter: brightness(1.08);
        transform: translateY(-1px);
    }



    div.stButton > button {
        border-radius: 12px !important;
        font-weight: 700 !important;
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
# Cache Excel Loading
# =========================
@st.cache_data(show_spinner=False)
def load_excel(file):
    return pd.read_excel(file)



# =========================
# Export Excel Function
# =========================
def convert_df_to_excel(dataframe):
    output = BytesIO()



    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        dataframe.to_excel(writer, index=False, sheet_name="Filtered_Reviews")



    return output.getvalue()



# =========================
# Cleaning Functions
# =========================
def clean_sentiment(value):
    value = str(value).strip().lower()



    if value in ["positive", "pos", "\u0625\u064a\u062c\u0627\u0628\u064a", "\u0627\u064a\u062c\u0627\u0628\u064a"]:
        return "Positive"
    elif value in ["negative", "neg", "\u0633\u0644\u0628\u064a"]:
        return "Negative"
    elif value in ["neutral", "neu", "\u0645\u062d\u0627\u064a\u062f"]:
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



# =========================
# Clear Filters Function
# =========================
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
        "review_search_keyword",
    ]



    for key in filter_keys:
        if key == "review_search_keyword":
            st.session_state[key] = ""
        else:
            st.session_state[key] = []



    st.session_state["analysis_ready"] = False
    st.session_state["last_filter_state"] = (
        tuple(),
        tuple(),
        tuple(),
        tuple(),
        tuple(),
        tuple(),
        tuple(),
        tuple(),
        "",
    )



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

# =========================
# Welcome Hero Image Section
# =========================
def get_welcome_image_base64():
    image_candidates = [
        "saudi_team_dashboard.png",
        "saudi_team_dashboard.jpg",
        "saudi_team_dashboard.jpeg",
        "saudi_team_dashboard.png.png",
        "saudi_team_dashboard.png(1).png",
        "saudi_team_dashboard.png(2).png",
    ]

    for image_name in image_candidates:
        image_path = Path(image_name)
        if image_path.exists():
            return base64.b64encode(image_path.read_bytes()).decode()

    return None


welcome_image_base64 = get_welcome_image_base64()

if welcome_image_base64:
    welcome_hero_html = f"""
    <style>
    .welcome-hero {{
        position: relative;
        min-height: 430px;
        border-radius: 28px;
        overflow: hidden;
        margin: 26px 0 28px 0;
        background-image:
            linear-gradient(90deg, rgba(15,118,110,0.88) 0%, rgba(8,145,178,0.58) 42%, rgba(0,0,0,0.10) 100%),
            url('data:image/png;base64,{welcome_image_base64}');
        background-size: cover;
        background-position: center;
        box-shadow: 0 18px 45px rgba(15, 118, 110, 0.26);
        animation: heroFadeIn 0.9s ease-out both;
    }}

    .welcome-hero::after {{
        content: "";
        position: absolute;
        top: -60%;
        left: -35%;
        width: 28%;
        height: 220%;
        background: linear-gradient(
            120deg,
            rgba(255,255,255,0.00) 0%,
            rgba(255,255,255,0.12) 35%,
            rgba(255,255,255,0.42) 50%,
            rgba(255,255,255,0.12) 65%,
            rgba(255,255,255,0.00) 100%
        );
        transform: rotate(22deg);
        animation: heroShine 5.5s infinite ease-in-out;
        pointer-events: none;
    }}

    .welcome-content {{
        position: absolute;
        left: 52px;
        top: 50%;
        transform: translateY(-50%);
        max-width: 660px;
        color: white;
        z-index: 2;
        animation: contentSlideUp 1s ease-out both;
    }}

    .welcome-badge {{
        display: inline-block;
        padding: 9px 16px;
        border-radius: 999px;
        background: rgba(255,255,255,0.18);
        border: 1px solid rgba(255,255,255,0.32);
        backdrop-filter: blur(6px);
        font-size: 15px;
        font-weight: 800;
        margin-bottom: 16px;
    }}

    .welcome-title {{
        font-size: 48px;
        font-weight: 950;
        margin: 0 0 14px 0;
        line-height: 1.08;
        text-shadow: 0 4px 18px rgba(0,0,0,0.28);
    }}

    .welcome-subtitle {{
        font-size: 23px;
        font-weight: 750;
        line-height: 1.45;
        margin: 0;
        text-shadow: 0 3px 12px rgba(0,0,0,0.24);
    }}

    .welcome-mini {{
        margin-top: 18px;
        font-size: 16px;
        font-weight: 700;
        opacity: 0.94;
    }}

    @keyframes heroFadeIn {{
        from {{ opacity: 0; transform: translateY(18px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}

    @keyframes contentSlideUp {{
        from {{ opacity: 0; transform: translateY(-42%); }}
        to {{ opacity: 1; transform: translateY(-50%); }}
    }}

    @keyframes heroShine {{
        0% {{ left: -45%; opacity: 0; }}
        18% {{ opacity: 0.9; }}
        42% {{ left: 125%; opacity: 0; }}
        100% {{ left: 125%; opacity: 0; }}
    }}

    @media (max-width: 900px) {{
        .welcome-hero {{ min-height: 360px; }}
        .welcome-content {{ left: 26px; right: 24px; max-width: none; }}
        .welcome-title {{ font-size: 36px; }}
        .welcome-subtitle {{ font-size: 18px; }}
    }}
    </style>

    <div class="welcome-hero">
        <div class="welcome-content">
            <div class="welcome-badge">AI-Powered Review Intelligence</div>
            <h2 class="welcome-title">Welcome!</h2>
            <p class="welcome-subtitle">Start exploring insights from Sehhaty reviews in seconds.</p>
            <div class="welcome-mini">Upload your file, choose filters, and discover actionable healthcare insights.</div>
        </div>
    </div>
    """
    st.markdown(welcome_hero_html, unsafe_allow_html=True)
else:
    st.markdown(
        """
        <style>
        .welcome-fallback {
            background: linear-gradient(135deg, #0891B2, #0F766E);
            color: white;
            padding: 38px 28px;
            border-radius: 24px;
            margin: 24px 0 28px 0;
            text-align: center;
            box-shadow: 0 16px 38px rgba(15, 118, 110, 0.24);
            position: relative;
            overflow: hidden;
        }
        .welcome-fallback::after {
            content: "";
            position: absolute;
            top: -60%;
            left: -40%;
            width: 30%;
            height: 220%;
            background: linear-gradient(120deg, transparent, rgba(255,255,255,0.45), transparent);
            transform: rotate(22deg);
            animation: fallbackShine 5s infinite ease-in-out;
        }
        @keyframes fallbackShine {
            0% { left: -45%; opacity: 0; }
            35% { left: 125%; opacity: 0.8; }
            100% { left: 125%; opacity: 0; }
        }
        </style>
        <div class="welcome-fallback">
            <h2 style="font-size:42px; font-weight:950; margin:0 0 12px 0;">Welcome!</h2>
            <p style="font-size:22px; font-weight:750; margin:0;">Start exploring insights from Sehhaty reviews in seconds.</p>
        </div>
        """,
        unsafe_allow_html=True
    )




uploaded_file = st.file_uploader("📂 Upload Excel file", type=["xlsx"])



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
    # Dashboard Filter Title
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
    box-shadow: 0 8px 22px rgba(15, 118, 110, 0.25);
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
    extra_themes = [
        x for x in get_sorted_unique(filter_df[theme_col])
        if x not in theme_options and x != "Unknown"
    ]
    theme_options = theme_options + extra_themes



    subtheme_options = [x for x in SUBTHEME_ORDER if x in existing_subthemes]
    extra_subthemes = [
        x for x in get_sorted_unique(filter_df[subtheme_col])
        if x not in subtheme_options and x != "Unknown"
    ]
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
        st.button(
            "🧹 Clear all filters",
            use_container_width=True,
            on_click=clear_dashboard_filters
        )



    with info_col:
        st.caption("No selection means All. Choose the filters and search keyword, then click Run Analysis to display the dashboard.")



    # =========================
    # Search Inside Reviews
    # =========================
    st.markdown("---")
    st.subheader("🔎 Search Inside Reviews")
    st.caption("Type any keyword to search within the filtered reviews, such as login, appointment, and error.")



    search_keyword = st.text_input(
        "Search keyword",
        placeholder="Example: login, error, appointment",
        key="review_search_keyword"
    )



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
        search_keyword.strip(),
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
        st.info("👆 Please choose the filters or search keyword, then click **Run Analysis** to display the dashboard charts and results.")
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



    if search_keyword.strip():
        analysis_source_df = analysis_source_df[
            analysis_source_df[text_col]
            .astype(str)
            .str.contains(search_keyword.strip(), case=False, na=False)
        ]



    analysis_df = analysis_source_df[
        (analysis_source_df["Sentiment_Clean"] != "Unknown") &
        (analysis_source_df[theme_col] != "Unknown") &
        (analysis_source_df[subtheme_col] != "Unknown")
    ].copy()



    if analysis_df.empty:
        st.warning("⚠️ No data available for the selected filters or search keyword. Please adjust your selections.")
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



    # =========================
    # Main Counts
    # =========================
    total_reviews = len(analysis_source_df)
    avg_rating = analysis_df[rating_col].mean()
    positive_count = (analysis_df["Sentiment_Clean"] == "Positive").sum()
    negative_count = (analysis_df["Sentiment_Clean"] == "Negative").sum()
    neutral_count = (analysis_df["Sentiment_Clean"] == "Neutral").sum()



    positive_rate = (positive_count / len(analysis_df) * 100) if len(analysis_df) > 0 else 0
    negative_rate = (negative_count / len(analysis_df) * 100) if len(analysis_df) > 0 else 0



    top_theme_name = (
        analysis_df[theme_col].value_counts().idxmax()
        if not analysis_df[theme_col].value_counts().empty
        else "N/A"
    )



    top_subtheme_name = (
        analysis_df[subtheme_col].value_counts().idxmax()
        if not analysis_df[subtheme_col].value_counts().empty
        else "N/A"
    )



    negative_df_for_summary = analysis_df[analysis_df["Sentiment_Clean"] == "Negative"]



    top_negative_theme_name = (
        negative_df_for_summary[theme_col].value_counts().idxmax()
        if not negative_df_for_summary.empty and not negative_df_for_summary[theme_col].value_counts().empty
        else "N/A"
    )



    # =========================
    # Executive Summary
    # =========================
    summary_html = f"""
<style>
.summary-box {{
    background: linear-gradient(135deg, #0891B2, #0F766E);
    color: white;
    padding: 22px 26px;
    border-radius: 20px;
    box-shadow: 0 10px 28px rgba(0,0,0,0.22);
    margin-top: 18px;
    margin-bottom: 18px;
}}
.summary-title {{
    font-size: 26px;
    font-weight: 850;
    margin-bottom: 12px;
}}
.summary-text {{
    font-size: 17px;
    line-height: 1.8;
}}
.summary-highlight {{
    font-weight: 850;
    color: #ECFEFF;
}}
</style>



<div class="summary-box">
    <div class="summary-title">📌 Executive Summary</div>
    <div class="summary-text">
        This dashboard analyzes <span class="summary-highlight">{total_reviews:,}</span> filtered Sehhaty app reviews.
        The average rating is <span class="summary-highlight">{avg_rating:.2f}</span>.
        Positive reviews represent <span class="summary-highlight">{positive_rate:.1f}%</span>,
        while negative reviews represent <span class="summary-highlight">{negative_rate:.1f}%</span>.
        The most common main theme is <span class="summary-highlight">{top_theme_name}</span>,
        and the most frequent subtheme is <span class="summary-highlight">{top_subtheme_name}</span>.
        The main area of concern among negative reviews is <span class="summary-highlight">{top_negative_theme_name}</span>.
    </div>
</div>
"""
    st.markdown(summary_html, unsafe_allow_html=True)



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



    # =========================
    # WOW Section: User Satisfaction + Review Storytelling + Top Keywords
    # =========================
    st.markdown("---")
    st.subheader("🤖 AI-Style Insights & User Voice")

    # Use the cleaned text column whenever it exists
    clean_text_col = "Content_Clean" if "Content_Clean" in analysis_df.columns else text_col

    satisfaction_level = max(0, min(100, int(round(positive_rate))))
    st.markdown("### 😊 User Satisfaction Level")
    st.progress(satisfaction_level)
    st.caption(f"Positive review rate: {positive_rate:.1f}% | Negative review rate: {negative_rate:.1f}%")

    # Dynamic insight sentence
    if positive_rate >= 70 and negative_rate < 30:
        smart_message = "Overall feedback is strongly positive, but the negative comments should still be reviewed to identify specific improvement opportunities."
    elif negative_rate >= 30:
        smart_message = "Negative feedback is relatively high, so priority should be given to the most frequent negative themes and subthemes."
    else:
        smart_message = "The feedback pattern is balanced, with opportunities to improve user experience by focusing on repeated themes and low-rating reviews."

    st.info(f"💡 Smart interpretation: {smart_message}")

    voice_col1, voice_col2 = st.columns(2)

    positive_reviews_for_voice = analysis_df[
        (analysis_df["Sentiment_Clean"] == "Positive") &
        (analysis_df[clean_text_col].astype(str).str.strip() != "")
    ].copy()

    negative_reviews_for_voice = analysis_df[
        (analysis_df["Sentiment_Clean"] == "Negative") &
        (analysis_df[clean_text_col].astype(str).str.strip() != "")
    ].copy()

    with voice_col1:
        st.markdown("### 🌟 Example Positive Review")
        if not positive_reviews_for_voice.empty:
            st.success(str(positive_reviews_for_voice.iloc[0][clean_text_col]))
        else:
            st.success("No positive review text available for the selected filters.")

    with voice_col2:
        st.markdown("### ⚠️ Example Negative Review")
        if not negative_reviews_for_voice.empty:
            st.error(str(negative_reviews_for_voice.iloc[0][clean_text_col]))
        else:
            st.error("No negative review text available for the selected filters.")

    # Top keyword and phrases based on cleaned content
    st.markdown("### 🔑 Top Keyword & Key Phrases from Filtered Reviews")
    try:
        from collections import Counter
        import html
        import re

        stop_words = set([
            "the", "and", "for", "with", "this", "that", "you", "your", "app", "application",
            "good", "very", "nice",
            "\u0645\u0646", "\u0641\u064a", "\u0639\u0644\u0649", "\u0627\u0644\u0649", "\u0625\u0644\u0649",
            "\u0639\u0646", "\u0645\u0639", "\u0647\u0630\u0627", "\u0647\u0630\u0647", "\u0627\u0646\u0647",
            "\u0623\u0646", "\u0625\u0646", "\u0644\u0627", "\u0645\u0627", "\u062a\u0645",
            "\u0643\u0644", "\u0644\u0643\u0645", "\u0634\u0643\u0631\u0627", "\u0634\u0643\u0631\u0627\u064b"
        ])

        one_word_items = []
        two_word_phrases = []
        three_word_phrases = []

        for sentence in analysis_df[clean_text_col].dropna().astype(str).tolist():
            words = re.findall(r"[\w\u0600-\u06FF]+", sentence.lower())
            words = [w for w in words if len(w) > 2 and w not in stop_words and not w.isdigit()]

            one_word_items.extend(words)

            for i in range(len(words) - 1):
                two_word_phrases.append(words[i] + " " + words[i + 1])

            for i in range(len(words) - 2):
                three_word_phrases.append(words[i] + " " + words[i + 1] + " " + words[i + 2])

        top_keyword = Counter(one_word_items).most_common(1)
        top_two_word_phrase = Counter(two_word_phrases).most_common(1)
        top_three_word_phrase = Counter(three_word_phrases).most_common(1)

        cards = []
        if top_keyword:
            cards.append(("Keyword", top_keyword[0][0], top_keyword[0][1]))
        if top_two_word_phrase:
            cards.append(("2-Word Phrase", top_two_word_phrase[0][0], top_two_word_phrase[0][1]))
        if top_three_word_phrase:
            cards.append(("3-Word Phrase", top_three_word_phrase[0][0], top_three_word_phrase[0][1]))

        if cards:
            phrase_cols = st.columns(3)
            for i, (label, phrase, count) in enumerate(cards):
                safe_phrase = html.escape(str(phrase))
                with phrase_cols[i]:
                    phrase_card_html = f"""
                    <div style="
                        background: linear-gradient(135deg, #0891B2, #0F766E);
                        color: white;
                        padding: 28px 20px;
                        border-radius: 20px;
                        text-align: center;
                        box-shadow: 0 10px 25px rgba(0,0,0,0.18);
                        min-height: 170px;
                    ">
                        <div style="font-size:18px; font-weight:800; opacity:0.95;">{label}</div>
                        <div style="font-size:30px; font-weight:900; margin-top:14px; word-break:break-word; line-height:1.35;">{safe_phrase}</div>
                        <div style="font-size:22px; font-weight:750; margin-top:10px;">{count:,}</div>
                    </div>
                    """
                    st.markdown(phrase_card_html, unsafe_allow_html=True)
        else:
            st.caption("No keyword or key phrase is available for the selected filters.")
    except Exception as e:
        st.caption(f"Top keyword and key phrases could not be generated: {e}")



    # =========================
    # Recommendations
    # =========================
    recommendations = []



    if negative_rate >= 30:
        recommendations.append("Prioritize negative feedback analysis because the negative review rate is relatively high.")
    else:
        recommendations.append("Continue monitoring negative feedback to identify early signs of user dissatisfaction.")



    if top_negative_theme_name != "N/A":
        recommendations.append(f"Focus improvement efforts on: {top_negative_theme_name}.")



    if top_subtheme_name != "N/A":
        recommendations.append(f"Investigate the most frequent subtheme: {top_subtheme_name}.")



    recommendations.append("Review low-rating comments to identify urgent usability, access, or technical issues.")
    recommendations.append("Use year, quarter, language, and sentiment filters to compare changes over time.")



    recommendation_items = "".join([f"<li>{item}</li>" for item in recommendations])



    recommendations_html = f"""
<style>
.recommendation-box {{
    background: #FFFFFF;
    color: #111827;
    padding: 22px 26px;
    border-radius: 20px;
    border-left: 7px solid #0F766E;
    box-shadow: 0 8px 24px rgba(15,23,42,0.12);
    margin-top: 14px;
    margin-bottom: 18px;
}}
.recommendation-title {{
    color: #0F766E;
    font-size: 24px;
    font-weight: 850;
    margin-bottom: 12px;
}}
.recommendation-box li {{
    font-size: 16px;
    margin-bottom: 8px;
    line-height: 1.6;
}}
</style>



<div class="recommendation-box">
    <div class="recommendation-title">💡 Recommended Actions</div>
    <ul>
        {recommendation_items}
    </ul>
</div>
"""
    st.markdown(recommendations_html, unsafe_allow_html=True)



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



    # =========================
    # Final Table Column Cleaning + Order
    # =========================
    # This keeps the cleaned review text column Content_Clean, not the original Content.
    final_column_rename = {
        "⭐Rating": "Rating",
        "📝Content": "Content",
        "💬DeveloperReply": "DeveloperReply",
        "📆Review_Year": "Review_Year",
        "📅Review_Month": "Review_Month",
        "📅Review_Day": "Review_Day",
        "⏰Review_Hour_12": "Review_Hour_12",
        "🌓Review_AM_PM": "Review_AM_PM",
        "🕰️Review_Period": "Review_Period",
        "🔢Comment_Length": "Comment_Length",
        "🧹Content_Clean": "Content_Clean",
        "🎯 Theme": "Theme",
        "🧩 Subtheme": "Subtheme",
        "😊 Sentiment": "Sentiment",
        "🌐 Language": "Language",
    }

    full_filtered_df = full_filtered_df.rename(columns=final_column_rename)

    # ✅ Add comment length from cleaned content if it is not already available
    if "Comment_Length" not in full_filtered_df.columns and "Content_Clean" in full_filtered_df.columns:
        full_filtered_df["Comment_Length"] = full_filtered_df["Content_Clean"].astype(str).str.len()

    preferred_order = [
        "Review_ID",
        "Rating",
        "Content_Clean",
        "DeveloperReply",
        "Language",
        "Theme",
        "Subtheme",
        "Sentiment",
        "Dashboard_Quarter",
        "Review_Year",
        "Review_Month",
        "Review_Day",
        "Review_Hour_12",
        "Review_AM_PM",
        "Review_Period",
        "Comment_Length",
    ]

    # Show only the required columns and remove any extra columns, such as:
    # Notes, Theme_GT, Subtheme_GT, Sentiment_GT, Dashboard_Year, Dashboard_Month, Sentiment_Clean, Content
    existing_cols = [col for col in preferred_order if col in full_filtered_df.columns]
    full_filtered_df = full_filtered_df[existing_cols]



    st.dataframe(full_filtered_df, width="stretch", hide_index=True)



    excel_file = convert_df_to_excel(full_filtered_df)



    st.download_button(
        label="⬇️ Download filtered reviews as Excel",
        data=excel_file,
        file_name="sehhaty_filtered_reviews.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )

    # =========================
    # Extra PDF Download Button
    # =========================
    st.markdown("""
    <style>
    div[data-testid="stDownloadButton"] > button {
        position: relative !important;
        overflow: hidden !important;
        background: linear-gradient(135deg, #0891B2, #0F766E) !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 16px !important;
        min-height: 56px !important;
        font-size: 17px !important;
        font-weight: 850 !important;
        box-shadow: 0 12px 28px rgba(15,118,110,0.28) !important;
        transition: all 0.25s ease !important;
    }
    div[data-testid="stDownloadButton"] > button:hover {
        transform: translateY(-3px) !important;
        filter: brightness(1.08) !important;
        box-shadow: 0 16px 34px rgba(15,118,110,0.38) !important;
    }
    div[data-testid="stDownloadButton"] > button::after {
        content: "";
        position: absolute;
        top: -70%;
        left: -60%;
        width: 42%;
        height: 240%;
        background: linear-gradient(120deg, rgba(255,255,255,0.00) 0%, rgba(255,255,255,0.18) 38%, rgba(255,255,255,0.70) 50%, rgba(255,255,255,0.18) 62%, rgba(255,255,255,0.00) 100%);
        transform: rotate(22deg);
        animation: downloadShine 4.6s infinite ease-in-out;
        pointer-events: none;
    }
    @keyframes downloadShine {
        0% { left: -65%; opacity: 0; }
        30% { opacity: 1; }
        55% { left: 130%; opacity: 0; }
        100% { left: 130%; opacity: 0; }
    }
    </style>
    """, unsafe_allow_html=True)

    def create_simple_pdf_report():
        report_lines = [
            "Sehhaty Smart Feedback Intelligence Platform",
            "Filtered Reviews Report",
            "",
            f"Total filtered reviews: {total_reviews:,}",
            f"Valid analysis rows: {len(analysis_df):,}",
            f"Average rating: {avg_rating:.2f}",
            f"Positive reviews: {positive_count:,} ({positive_rate:.1f}%)",
            f"Negative reviews: {negative_count:,} ({negative_rate:.1f}%)",
            f"Neutral reviews: {neutral_count:,}",
            "",
            f"Top theme: {top_theme_name}",
            f"Top subtheme: {top_subtheme_name}",
            f"Main negative theme: {top_negative_theme_name}",
            "",
            "Recommended actions:",
        ]

        for item in recommendations:
            report_lines.append(f"- {item}")

        def pdf_escape(value):
            value = str(value).encode("latin-1", "replace").decode("latin-1")
            return value.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")

        text_commands = ["BT", "/F1 18 Tf", "72 750 Td", f"({pdf_escape(report_lines[0])}) Tj", "/F1 11 Tf", "0 -28 Td"]
        for line in report_lines[1:]:
            text_commands.append(f"({pdf_escape(line)}) Tj")
            text_commands.append("0 -16 Td")
        text_commands.append("ET")
        stream = "\n".join(text_commands).encode("latin-1", "replace")

        objects = [
            b"<< /Type /Catalog /Pages 2 0 R >>",
            b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
            b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
            b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
            b"<< /Length " + str(len(stream)).encode() + b" >>\nstream\n" + stream + b"\nendstream",
        ]

        pdf = bytearray(b"%PDF-1.4\n")
        offsets = [0]
        for index, obj in enumerate(objects, start=1):
            offsets.append(len(pdf))
            pdf.extend(f"{index} 0 obj\n".encode())
            pdf.extend(obj)
            pdf.extend(b"\nendobj\n")

        xref_start = len(pdf)
        pdf.extend(f"xref\n0 {len(objects) + 1}\n".encode())
        pdf.extend(b"0000000000 65535 f \n")
        for offset in offsets[1:]:
            pdf.extend(f"{offset:010d} 00000 n \n".encode())
        pdf.extend(f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref_start}\n%%EOF".encode())
        return bytes(pdf)

    pdf_file = create_simple_pdf_report()

    st.download_button(
        label="📄 Download PDF Report",
        data=pdf_file,
        file_name="sehhaty_dashboard_report.pdf",
        mime="application/pdf",
        use_container_width=True
    )
