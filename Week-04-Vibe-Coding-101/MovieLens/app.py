"""MovieLens dashboard — Week 4 vibe-coding homework."""

from html import escape
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(
    page_title="MovieLens · Screening Room",
    page_icon="🎞️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# --- palette ----------------------------------------------------------------
# One warm accent (marquee amber) on a near-black stage. A cool slate is the
# only second hue, used strictly for "below average" in the diverging chart.

INK = "#0d0e12"
PANEL = "#15171d"
LINE = "#262a33"
TEXT = "#ece6da"
MUTED = "#8c919c"
FAINT = "#5a5f6a"
AMBER = "#f0a83a"
AMBER_DIM = "#8a6326"
SLATE = "#6f8db5"

# --- styles -----------------------------------------------------------------

st.markdown(
    f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,600&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');

:root {{
  --ink:{INK}; --panel:{PANEL}; --line:{LINE}; --text:{TEXT};
  --muted:{MUTED}; --faint:{FAINT}; --amber:{AMBER}; --slate:{SLATE};
}}
html, body, [data-testid="stAppViewContainer"], .stApp {{
  background: var(--ink); color: var(--text);
  font-family: 'Inter', system-ui, sans-serif;
}}
[data-testid="stHeader"], [data-testid="stSidebar"],
[data-testid="collapsedControl"], footer, #MainMenu {{ display:none !important; }}
.block-container {{ max-width: 1180px; padding: 3.2rem 1.5rem 5rem; }}

/* hero */
.eyebrow {{
  font-family:'JetBrains Mono', monospace; font-size:.72rem; letter-spacing:.18em;
  text-transform:uppercase; color:var(--amber);
}}
.hero h1 {{
  font-family:'Fraunces', Georgia, serif; font-weight:400; font-size:clamp(2.2rem,5vw,3.9rem);
  line-height:1.04; letter-spacing:-.02em; margin:.6rem 0 1rem; color:var(--text);
}}
.hero h1 em {{ font-style:italic; color:var(--amber); }}
.hero p {{ color:var(--muted); max-width:620px; font-size:1.02rem; line-height:1.6; }}

/* filter bar */
.filter-label {{
  font-family:'JetBrains Mono', monospace; font-size:.68rem; letter-spacing:.14em;
  text-transform:uppercase; color:var(--faint); margin-bottom:.25rem;
}}
[data-testid="stPopover"] button, [data-testid="stBaseButton-secondary"] {{
  background:var(--panel) !important; border:1px solid var(--line) !important;
  color:var(--text) !important; border-radius:999px !important;
}}
[data-testid="stSlider"] [role="slider"] {{ background:var(--amber) !important; box-shadow:none !important; }}

/* stat strip */
.stats {{
  display:grid; grid-template-columns:repeat(4,1fr); gap:1px; background:var(--line);
  border:1px solid var(--line); border-radius:14px; overflow:hidden; margin:1.4rem 0 3.2rem;
}}
.stat {{ background:var(--panel); padding:1.1rem 1.3rem; }}
.stat .v {{ font-family:'Fraunces', serif; font-size:2rem; line-height:1.1; color:var(--text); }}
.stat .v small {{ font-size:1rem; color:var(--muted); }}
.stat .k {{ font-size:.78rem; color:var(--muted); margin-top:.25rem; }}
@media (max-width: 720px) {{ .stats {{ grid-template-columns:repeat(2,1fr); }} }}

/* chapters */
.chapter {{ border-top:1px solid var(--line); padding-top:1.6rem; margin-top:2.6rem; }}
.chapter .num {{
  font-family:'JetBrains Mono', monospace; font-size:.72rem; letter-spacing:.16em;
  color:var(--amber); text-transform:uppercase;
}}
.chapter h2 {{
  font-family:'Fraunces', serif; font-weight:400; font-size:1.9rem; line-height:1.15;
  margin:.35rem 0 .8rem; color:var(--text); letter-spacing:-.01em;
}}
.chapter .q {{ color:var(--muted); font-size:.95rem; line-height:1.55; }}
.answer {{
  margin-top:1.1rem; padding:1rem 1.1rem; background:var(--panel);
  border-left:2px solid var(--amber); border-radius:0 10px 10px 0;
  font-size:.93rem; line-height:1.55; color:var(--text);
}}
.answer b {{ color:var(--amber); font-weight:600; }}
.method {{ margin-top:.9rem; font-size:.8rem; line-height:1.55; color:var(--faint); }}
.method code {{ background:var(--panel); color:var(--muted); padding:1px 5px; border-radius:4px; }}

/* ranked list */
.rank {{ display:flex; gap:1rem; align-items:baseline; padding:.75rem 0; border-bottom:1px solid var(--line); }}
.rank:last-child {{ border-bottom:none; }}
.rank .n {{ font-family:'Fraunces', serif; font-size:1.6rem; color:var(--faint); width:1.4rem; }}
.rank .t {{ flex:1; font-size:.95rem; color:var(--text); }}
.rank .meta {{ font-family:'JetBrains Mono', monospace; font-size:.78rem; color:var(--muted); white-space:nowrap; }}
.rank .meta b {{ color:var(--text); font-weight:500; }}
.tag {{
  font-family:'JetBrains Mono', monospace; font-size:.62rem; letter-spacing:.08em;
  text-transform:uppercase; padding:2px 7px; border-radius:999px; margin-left:.5rem;
  border:1px solid var(--line); color:var(--muted); vertical-align:middle;
}}
.tag.out {{ border-color:var(--slate); color:var(--slate); }}
.tag.in {{ border-color:var(--amber); color:var(--amber); }}
.list-head {{
  font-family:'JetBrains Mono', monospace; font-size:.72rem; letter-spacing:.14em;
  text-transform:uppercase; color:var(--muted); margin-bottom:.3rem;
}}
.list-head span {{ color:var(--amber); }}
.foot {{ margin-top:4rem; color:var(--faint); font-size:.78rem; }}
</style>
""",
    unsafe_allow_html=True,
)

# --- plotly look ------------------------------------------------------------

PLOT_CONFIG = {"displayModeBar": False, "responsive": True}


def style(fig: go.Figure, height: int = 460) -> go.Figure:
    fig.update_layout(
        height=height,
        margin=dict(l=8, r=24, t=8, b=8),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color=MUTED, size=12),
        hoverlabel=dict(bgcolor=PANEL, bordercolor=LINE, font=dict(color=TEXT, family="Inter")),
        showlegend=False,
        bargap=0.28,
    )
    fig.update_xaxes(gridcolor=LINE, zeroline=False, linecolor=LINE, tickfont=dict(color=FAINT))
    fig.update_yaxes(gridcolor="rgba(0,0,0,0)", zeroline=False, linecolor=LINE, tickfont=dict(color=MUTED))
    return fig


# --- data loading -----------------------------------------------------------

DATA_CANDIDATES = [
    Path(__file__).resolve().parent / "data" / "movie_ratings.csv",
    Path(__file__).resolve().parent.parent / "data" / "movie_ratings.csv",
]


@st.cache_data
def load_ratings() -> pd.DataFrame:
    path = next((p for p in DATA_CANDIDATES if p.exists()), None)
    if path is None:
        st.error("Could not find movie_ratings.csv next to this app or in ../data/.")
        st.stop()

    df = pd.read_csv(path)
    df["year"] = pd.to_numeric(df["year"], errors="coerce")
    return df


@st.cache_data
def explode_genres(df: pd.DataFrame) -> pd.DataFrame:
    """One row per (rating, genre). A movie with 3 genres contributes 3 rows.

    Genre breakdown counts *unique movies* after this explode, so a multi-genre
    movie is counted once in each of its genres, not once overall and not once
    per rating. Satisfaction / averages use the exploded *ratings* so every
    star a user gave still counts.
    """
    out = df.copy()
    out["genre"] = out["genres"].fillna("unknown").str.split("|")
    return out.explode("genre")


ratings = load_ratings()
movie_catalog = ratings.drop_duplicates("movie_id").copy()
movie_catalog["genre"] = movie_catalog["genres"].fillna("unknown").str.split("|")
movie_genres = movie_catalog.explode("genre")

all_genres = sorted(movie_genres["genre"].dropna().unique())
year_min = int(ratings["year"].min())
year_max = int(ratings["year"].max())

# --- hero -------------------------------------------------------------------

st.markdown(
    f"""
<div class="hero">
  <div class="eyebrow">MovieLens 100K &nbsp;·&nbsp; GroupLens &nbsp;·&nbsp; {year_min}–{year_max}</div>
  <h1>What {len(ratings):,} ratings<br>say about <em>the movies.</em></h1>
  <p>Four questions about genre, taste and time, asked of {ratings['user_id'].nunique():,}
  viewers and {ratings['movie_id'].nunique():,} films. Narrow the reel below and
  every chart re-cuts itself.</p>
</div>
""",
    unsafe_allow_html=True,
)

# --- filter bar -------------------------------------------------------------

f1, f2, f3 = st.columns([1, 1.4, 1.4], gap="large", vertical_alignment="bottom")

with f1:
    if "genres" not in st.session_state:
        st.session_state["genres"] = all_genres
    picked = st.session_state["genres"]
    st.markdown('<div class="filter-label">Genres</div>', unsafe_allow_html=True)
    label = "All genres" if len(picked) == len(all_genres) else f"{len(picked)} of {len(all_genres)} genres"
    with st.popover(label):
        a, b = st.columns(2)
        if a.button("Select all"):
            st.session_state["genres"] = all_genres
            st.rerun()
        if b.button("Clear"):
            st.session_state["genres"] = []
            st.rerun()
        selected_genres = st.pills(
            "Genres",
            options=all_genres,
            selection_mode="multi",
            key="genres",
            label_visibility="collapsed",
            help="Multi-genre movies stay in if *any* selected genre matches.",
        )
with f2:
    st.markdown('<div class="filter-label">Release years</div>', unsafe_allow_html=True)
    year_range = st.slider(
        "Release year range",
        min_value=year_min,
        max_value=year_max,
        value=(year_min, year_max),
        label_visibility="collapsed",
    )
with f3:
    st.markdown('<div class="filter-label">Rating floor for “best movies”</div>', unsafe_allow_html=True)
    rating_floor = st.slider(
        "Minimum ratings",
        min_value=10,
        max_value=250,
        value=50,
        step=10,
        label_visibility="collapsed",
        help="Question 4 floor. Compare 50 vs 150 by moving this slider.",
    )

selected_genres = list(selected_genres or [])
if not selected_genres:
    st.info("No genres selected — open the Genres menu and pick at least one.")
    st.stop()

year_lo, year_hi = year_range
in_years = ratings["year"].between(year_lo, year_hi) | ratings["year"].isna()
filtered = ratings[in_years]
keep_ids = set(
    movie_genres.loc[movie_genres["genre"].isin(selected_genres), "movie_id"]
)
filtered = filtered[filtered["movie_id"].isin(keep_ids)]
if filtered.empty:
    st.info("Nothing matches these filters. Widen the year range or add genres.")
    st.stop()

filtered_exploded = explode_genres(filtered)
filtered_movies = movie_genres[
    movie_genres["movie_id"].isin(filtered["movie_id"].unique())
    & movie_genres["genre"].isin(selected_genres)
]
overall_mean = filtered["rating"].mean()

# --- stat strip -------------------------------------------------------------

st.markdown(
    f"""
<div class="stats">
  <div class="stat"><div class="v">{len(filtered):,}</div><div class="k">ratings in view</div></div>
  <div class="stat"><div class="v">{filtered['movie_id'].nunique():,}</div><div class="k">films</div></div>
  <div class="stat"><div class="v">{filtered['user_id'].nunique():,}</div><div class="k">viewers</div></div>
  <div class="stat"><div class="v">{overall_mean:.2f}<small> / 5</small></div><div class="k">mean rating</div></div>
</div>
""",
    unsafe_allow_html=True,
)


def chapter(num: str, title: str, question: str, answer: str, method: str = "") -> None:
    st.markdown(
        f"""
<div class="chapter">
  <div class="num">{num}</div>
  <h2>{title}</h2>
  <div class="q">{question}</div>
  <div class="answer">{answer}</div>
  {f'<div class="method">{method}</div>' if method else ''}
</div>
""",
        unsafe_allow_html=True,
    )


# --- q1 genre breakdown -----------------------------------------------------

genre_counts = (
    filtered_movies.groupby("genre")["movie_id"]
    .nunique()
    .sort_values(ascending=True)
    .reset_index(name="movies")
)
n_films = filtered["movie_id"].nunique()
top_g = genre_counts.iloc[-1]

text_col, chart_col = st.columns([1, 1.9], gap="large")
with text_col:
    chapter(
        "Reel 01 · Genre breakdown",
        f"{escape(top_g['genre'])} leads the catalog.",
        "What’s the distribution of genres among the movies that were rated?",
        f"<b>{escape(top_g['genre'])}</b> tags {top_g['movies']:,} of {n_films:,} films "
        f"({top_g['movies'] / n_films:.0%}). Bars sum to more than the film count because "
        "one movie can wear several genres.",
        "Method: <code>genres</code> is pipe-separated (<code>Action|Thriller</code>). "
        "Each movie is split on <code>|</code> and counted <b>once per genre</b>. Counts are "
        "unique movies, not ratings. <code>unknown</code> = two movies with no usable label.",
    )
with chart_col:
    st.markdown('<div style="height:2.6rem"></div>', unsafe_allow_html=True)
    fig1 = go.Figure(
        go.Bar(
            x=genre_counts["movies"],
            y=genre_counts["genre"],
            orientation="h",
            marker=dict(color=AMBER, cornerradius=4),
            text=genre_counts["movies"],
            textposition="outside",
            textfont=dict(color=MUTED, family="JetBrains Mono", size=11),
            cliponaxis=False,
            hovertemplate="<b>%{y}</b><br>%{x:,} films<extra></extra>",
        )
    )
    style(fig1, height=max(320, 26 * len(genre_counts)))
    fig1.update_xaxes(showgrid=False, showticklabels=False)
    st.plotly_chart(fig1, config=PLOT_CONFIG)

# --- q2 genre satisfaction --------------------------------------------------

genre_means = (
    filtered_exploded.groupby("genre")["rating"]
    .agg(mean_rating="mean", n_ratings="size")
    .reset_index()
)
genre_means = genre_means[genre_means["genre"].isin(selected_genres)]
genre_means = genre_means.sort_values("mean_rating", ascending=True)
# "unknown" is two films; don't let it headline the answer.
labelled = genre_means[genre_means["genre"] != "unknown"]
labelled = labelled if len(labelled) else genre_means
hi = labelled.iloc[-1]
lo = labelled.iloc[0]

text_col, chart_col = st.columns([1, 1.9], gap="large")
with text_col:
    chapter(
        "Reel 02 · Genre satisfaction",
        f"{escape(hi['genre'])} on top, {escape(lo['genre'])} at the bottom.",
        "Which genres have the highest average rating? Which have the lowest?",
        f"Highest: <b>{escape(hi['genre'])}</b> at {hi['mean_rating']:.2f}. "
        f"Lowest: <b>{escape(lo['genre'])}</b> at {lo['mean_rating']:.2f}. "
        f"The dashed line is the overall mean ({overall_mean:.2f}); amber sits above it, slate below.",
        "Method: mean of <b>individual ratings</b> after splitting genres, so a 5★ on a "
        "Drama|War movie lifts both. Hover a dot to see how many ratings back it up.",
    )
with chart_col:
    st.markdown('<div style="height:2.6rem"></div>', unsafe_allow_html=True)
    above = genre_means["mean_rating"] >= overall_mean
    dot_colors = [AMBER if a else SLATE for a in above]
    fig2 = go.Figure()
    for _, r in genre_means.iterrows():
        fig2.add_shape(
            type="line", x0=overall_mean, x1=r["mean_rating"], y0=r["genre"], y1=r["genre"],
            line=dict(color=AMBER_DIM if r["mean_rating"] >= overall_mean else "#3b4a60", width=2),
        )
    fig2.add_trace(
        go.Scatter(
            x=genre_means["mean_rating"],
            y=genre_means["genre"],
            mode="markers",
            marker=dict(size=11, color=dot_colors, line=dict(color=INK, width=2)),
            customdata=genre_means["n_ratings"],
            hovertemplate="<b>%{y}</b><br>mean %{x:.3f}<br>%{customdata:,} ratings<extra></extra>",
        )
    )
    fig2.add_vline(x=overall_mean, line=dict(color=FAINT, width=1, dash="dot"))
    style(fig2, height=max(320, 26 * len(genre_means)))
    pad = 0.08
    fig2.update_xaxes(
        range=[genre_means["mean_rating"].min() - pad, genre_means["mean_rating"].max() + pad],
        title=dict(text="Mean rating (1–5)", font=dict(color=FAINT, size=11)),
    )
    st.plotly_chart(fig2, config=PLOT_CONFIG)

# --- q3 ratings over time ---------------------------------------------------

by_year = (
    filtered.dropna(subset=["year"])
    .assign(release_year=lambda d: d["year"].astype(int))
    .groupby("release_year")
    .agg(mean_rating=("rating", "mean"), n_ratings=("rating", "size"))
    .reset_index()
)
old = by_year[by_year["release_year"] < 1980]
new = by_year[by_year["release_year"] >= 1990]
old_mean = (old["mean_rating"] * old["n_ratings"]).sum() / max(old["n_ratings"].sum(), 1)
new_mean = (new["mean_rating"] * new["n_ratings"]).sum() / max(new["n_ratings"].sum(), 1)

chapter(
    "Reel 03 · Ratings over time",
    (
        "Older films score higher — survivorship at work."
        if len(old) and len(new) and old_mean > new_mean
        else "How taste shifts with release year."
    ),
    "How has the mean rating changed across <b>movie release years</b> "
    "(the <code>year</code> column, not when the user rated it)?",
    (
        f"Pre-1980 releases average <b>{old_mean:.2f}</b>; 1990s releases average "
        f"<b>{new_mean:.2f}</b>. Viewers in 1997–98 mostly sought out old films that were "
        "already known to be good, while new releases got rated regardless."
        if len(old) and len(new)
        else "Widen the year range to compare older and newer releases."
    ),
    "Dot size = number of ratings that year. Early years with a handful of ratings swing wildly — "
    "trust the big dots.",
)
fig3 = go.Figure()
fig3.add_trace(
    go.Scatter(
        x=by_year["release_year"],
        y=by_year["mean_rating"],
        mode="lines",
        line=dict(color=AMBER, width=2),
        fill="tozeroy",
        fillcolor="rgba(240,168,58,0.06)",
        hoverinfo="skip",
    )
)
size = 5 + 17 * (by_year["n_ratings"] / by_year["n_ratings"].max()) ** 0.5
fig3.add_trace(
    go.Scatter(
        x=by_year["release_year"],
        y=by_year["mean_rating"],
        mode="markers",
        marker=dict(size=size, color=AMBER, opacity=0.85, line=dict(color=INK, width=2)),
        customdata=by_year["n_ratings"],
        hovertemplate="<b>%{x}</b><br>mean %{y:.2f}<br>%{customdata:,} ratings<extra></extra>",
    )
)
fig3.add_hline(y=overall_mean, line=dict(color=FAINT, width=1, dash="dot"))
style(fig3, height=380)
fig3.update_yaxes(range=[1, 5.2], gridcolor=LINE, tickfont=dict(color=FAINT), dtick=1)
fig3.update_xaxes(showgrid=False)
fig3.update_layout(hovermode="closest")
st.plotly_chart(fig3, config=PLOT_CONFIG)

# --- q4 best movies with a floor --------------------------------------------

movie_stats = (
    filtered.groupby(["movie_id", "title"], as_index=False)
    .agg(mean_rating=("rating", "mean"), n_ratings=("rating", "size"))
)


def top5(floor: int) -> pd.DataFrame:
    out = movie_stats[movie_stats["n_ratings"] >= floor].copy()
    return out.sort_values(
        ["mean_rating", "n_ratings"], ascending=[False, False]
    ).head(5)


top_floor = top5(rating_floor)
top_50 = top5(50)
top_150 = top5(150)
dropped = [t for t in top_50["title"] if t not in set(top_150["title"])]
added = [t for t in top_150["title"] if t not in set(top_50["title"])]

chapter(
    "Reel 04 · Best movies, with a floor",
    "Raise the bar, lose the cult hits.",
    f"Top 5 by mean rating among films with at least <b>{rating_floor}</b> ratings "
    "(set by the floor slider above). Ties broken by rating count.",
    (
        f"Going from 50 to 150 ratings drops <b>{len(dropped)}</b> of the top 5 — "
        + (", ".join(escape(t) for t in dropped) if dropped else "none")
        + ". Small-crowd favourites fall away and widely rated classics take their place."
    ),
)

chart_col, list_col = st.columns([1.5, 1], gap="large")
with chart_col:
    d = top_floor.sort_values("mean_rating", ascending=True).assign(
        title=lambda x: x["title"].where(x["title"].str.len() <= 30, x["title"].str[:28] + "…")
    )
    fig4 = go.Figure()
    for _, r in d.iterrows():
        fig4.add_shape(
            type="line", x0=d["mean_rating"].min() - 0.1, x1=r["mean_rating"],
            y0=r["title"], y1=r["title"], line=dict(color=LINE, width=2),
        )
    fig4.add_trace(
        go.Scatter(
            x=d["mean_rating"],
            y=d["title"],
            mode="markers+text",
            marker=dict(size=14, color=AMBER, line=dict(color=INK, width=2)),
            text=[f"{v:.2f}" for v in d["mean_rating"]],
            textposition="middle right",
            textfont=dict(color=TEXT, family="JetBrains Mono", size=11),
            customdata=d["n_ratings"],
            hovertemplate="<b>%{y}</b><br>mean %{x:.3f}<br>%{customdata:,} ratings<extra></extra>",
            cliponaxis=False,
        )
    )
    style(fig4, height=320)
    if len(d):
        fig4.update_xaxes(range=[d["mean_rating"].min() - 0.1, d["mean_rating"].max() + 0.12],
                          showgrid=False, title=dict(text="Mean rating", font=dict(color=FAINT, size=11)))
    st.plotly_chart(fig4, config=PLOT_CONFIG)
    st.caption("Axis is zoomed in: the top 5 sit within a few tenths of a star.")


def ranked(df: pd.DataFrame, heading: str, other: set, tag_cls: str, tag_text: str) -> str:
    tag = f'<span class="tag {tag_cls}">{tag_text}</span>'
    rows = "".join(
        f'<div class="rank"><div class="n">{i}</div>'
        f'<div class="t">{escape(r.title)}{tag if r.title not in other else ""}</div>'
        f'<div class="meta"><b>{r.mean_rating:.2f}</b> · {r.n_ratings:,}</div></div>'
        for i, r in enumerate(df.itertuples(), start=1)
    )
    return f'<div class="list-head">{heading}</div>{rows or "<div class=q>No films clear this floor.</div>"}'


with list_col:
    st.markdown(
        ranked(top_50, "Floor <span>50</span>", set(top_150["title"]), "out", "drops at 150"),
        unsafe_allow_html=True,
    )
    st.markdown('<div style="height:1.4rem"></div>', unsafe_allow_html=True)
    st.markdown(
        ranked(top_150, "Floor <span>150</span>", set(top_50["title"]), "in", "new"),
        unsafe_allow_html=True,
    )

st.markdown(
    '<div class="foot">Data: GroupLens MovieLens 100K. Mean ratings on a 1–5 star scale. '
    "Built for CTP Week 4.</div>",
    unsafe_allow_html=True,
)
