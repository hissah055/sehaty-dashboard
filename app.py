import base64
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
# Fixed Plot Style
# =========================
PLOT_TEMPLATE = "plotly_white"
PLOT_FONT_COLOR = "#FFFFFF"
PLOT_BG_COLOR = "#0C848F"   # Teal chart background matching the main header
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


def remove_private_columns(dataframe):
    private_cols = []

    for col in dataframe.columns:
        col_text = str(col).strip().lower()
        col_clean = (
            col_text
            .replace(" ", "")
            .replace("_", "")
            .replace("-", "")
        )

        if (
            "username" in col_clean
            or col_clean in ["name", "reviewer", "author"]
            or "reviewer" in col_clean
            or "author" in col_clean
        ):
            private_cols.append(col)

    return dataframe.drop(columns=private_cols, errors="ignore")


if uploaded_file:
    df = load_excel(uploaded_file)

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
    # Data Preview
    # =========================
    st.subheader("🔍 Data Preview")
    st.caption("Showing a preview with usernames removed for privacy.")

    preview_df = df.head(5).copy()
    preview_df = remove_private_columns(preview_df)
    preview_df.insert(0, "Review_ID", range(1, len(preview_df) + 1))
    preview_df = preview_df.reset_index(drop=True)

    st.dataframe(preview_df, width="stretch", hide_index=True)

    if st.button("🚀 Start Analysis"):

        progress_bar = st.progress(0)
        status_text = st.empty()

        status_text.write("⏳ Preparing data...")
        progress_bar.progress(15)

        df[text_col] = df[text_col].fillna("").astype(str)
        df[theme_col] = df[theme_col].apply(clean_category)
        df[subtheme_col] = df[subtheme_col].apply(clean_category)
        df[language_col] = df[language_col].apply(clean_category)
        df[rating_col] = pd.to_numeric(df[rating_col], errors="coerce")

        status_text.write("🧹 Cleaning sentiment, themes, and subthemes...")
        progress_bar.progress(35)

        df["Sentiment_Clean"] = df[sentiment_col].apply(clean_sentiment)

        analysis_df = df[
            (df["Sentiment_Clean"] != "Unknown") &
            (df[theme_col] != "Unknown") &
            (df[subtheme_col] != "Unknown")
        ].copy()

        status_text.write("📊 Calculating key indicators...")
        progress_bar.progress(55)

        total_reviews = len(df)
        avg_rating = analysis_df[rating_col].mean()
        positive_count = (analysis_df["Sentiment_Clean"] == "Positive").sum()
        negative_count = (analysis_df["Sentiment_Clean"] == "Negative").sum()
        neutral_count = (analysis_df["Sentiment_Clean"] == "Neutral").sum()

        status_text.write("🎨 Building interactive charts...")
        progress_bar.progress(80)

        progress_bar.progress(100)
        status_text.write("✅ Analysis completed successfully!")

        st.success("✅ Analysis Completed!")

        c1, c2, c3, c4, c5 = st.columns(5)

        c1.metric("Total Reviews", f"{total_reviews:,}")
        c2.metric("Avg Rating", f"{avg_rating:.2f}")
        c3.metric("Positive", f"{positive_count:,}")
        c4.metric("Negative", f"{negative_count:,}")
        c5.metric("Neutral", f"{neutral_count:,}")

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
        # Data Sample
        # =========================
        st.subheader("📄 Data Sample")
        st.caption("Showing a sample of 20 anonymized rows only for faster performance.")

        sample_df = analysis_df.head(20).copy()
        sample_df.insert(0, "Review_ID", range(1, len(sample_df) + 1))
        sample_df = remove_private_columns(sample_df)
        sample_df = sample_df.reset_index(drop=True)

        st.dataframe(sample_df, width="stretch", hide_index=True)
