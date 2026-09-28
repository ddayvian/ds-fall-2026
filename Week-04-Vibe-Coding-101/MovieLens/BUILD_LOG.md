# MovieLens dashboard — raw build log

Scratch notes from building this with Cursor. Not a polished writeup.

---

## Moment 1 — starting prompt

**Prompt I gave:**
> create an extra file within this Week-04-Vibe-Coding-101 called MovieLens and in this file do the instructions that are given from Week4_Vibe_Coding_Dashboard_Build.md

**What the AI did first:**
Read the homework markdown, inspected `data/movie_ratings.csv` (100k rows; columns are `user_id` / `movie_id` not the `userId`/`movieId` names in the prompt), then scaffolded a Streamlit app under `MovieLens/` instead of a single empty file — because Task 2 needs `app.py` + `requirements.txt`.

**What I kept / would change:**
Kept the folder layout. Data stays in `Week-04-Vibe-Coding-101/data/` (already in the repo); `app.py` looks next to itself and then one directory up so Streamlit Cloud can still find the CSV.

---

## Moment 2 — genre explode, before any counts

**Prompt / instruction in the homework:**
> Movies can have multiple genres — have the AI explain how it handled that before it counts anything.

**First-pass choice:**
Split `genres` on `|` and explode. Q1 counts **unique movies** per genre (a Drama|Crime movie +1 Drama and +1 Crime, regardless of how many times it was rated). Q2 averages **ratings** after the same explode (each user star counts for every genre tag on that film).

**Why not change it:**
Q1 says "movies that were rated," so movie-level. Q2 says "average rating," so rating-level. If both used movie-level means, popular films wouldn't dominate the genre mean — next week's lecture can call that out.

**Chart type:**
Horizontal bar, sorted by value. Homework chart table warns that AI defaults to a pie with ~18 slices; I didn't use a pie.

---

## Moment 3 — Q3 year column + Q4 floor

**Ambiguity:**
"Mean rating changed across movie release years" could be confused with `rating_year` (when the user rated). Used `year` (release). Dropped 30 ratings with missing year.

**Q4 floor:**
Grouped by `movie_id` + `title`, mean + count, filter `n >= floor`, top 5 by mean then by count. Sidebar slider defaults to 50; page also prints the 50 vs 150 tables so the "what changes" question is visible without moving the slider.

**Widgets:**
Genre multi-select, release-year range, minimum-ratings slider.

---

## Deploy notes (Task 2)

Streamlit Cloud builds from GitHub, not this laptop.

1. Commit `MovieLens/app.py`, `MovieLens/requirements.txt`, and the existing `data/movie_ratings.csv`.
2. Push to the public repo (`https://github.com/ddayvian/ds-fall-2026`).
3. On [share.streamlit.io](https://share.streamlit.io): repo `ddayvian/ds-fall-2026`, branch `main`, main file path `Week-04-Vibe-Coding-101/MovieLens/app.py`.
4. Open the `*.streamlit.app` URL in a private window before submitting.

---

## Moment 4 — UI/UX redesign

**Prompt I gave:**
> do a better ux ui, avoid looking like the other MovieLens Streamlit dashboards, change color if needed

**What changed:**
Dropped the default Streamlit look (sidebar + numbered headers + stock Plotly). Dark "screening room" theme with one amber accent, serif headlines, filters in one row above the charts (genre pills in a popover), a stat strip, and each question as a "reel" with a written answer computed from the filtered data. Q2 became a dot plot diverging from the overall mean; Q3 sizes dots by rating count so noisy early years read as noisy; Q4 is a zoomed dot plot plus ranked 50 vs 150 lists that tag which titles drop out.
