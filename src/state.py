"""Cached data + sidebar filter state shared by every page."""

import pandas as pd
import streamlit as st

from src.data import build_cube, hashtag_table, load_posts

FILTER_KEYS = {
    "f_format": "Post Type",
    "f_month": "Month Name",
    "f_campaign": "Campaign Type",
    "f_source": "Engagement Source",
}


@st.cache_data(show_spinner="Preparing 50,000 posts…")
def get_data():
    posts = load_posts()
    tags = hashtag_table(posts)
    return posts, tags


def sidebar_filters():
    posts, tags = get_data()
    st.sidebar.header("Filters")
    months = posts.drop_duplicates("Month").sort_values("Month")["Month Name"].tolist()
    st.sidebar.multiselect("Post format", sorted(posts["Post Type"].unique()), key="f_format",
                           placeholder="All formats")
    st.sidebar.multiselect("Month", months, key="f_month", placeholder="All months")
    st.sidebar.multiselect("Hashtag", sorted(tags["Hashtag"].unique()), key="f_tag",
                           placeholder="All hashtags")
    st.sidebar.multiselect("Campaign", sorted(posts["Campaign Type"].unique()), key="f_campaign",
                           placeholder="All campaigns")
    st.sidebar.multiselect("Source", sorted(posts["Engagement Source"].unique()), key="f_source",
                           placeholder="All sources")
    st.sidebar.button("Reset filters", on_click=_reset)


def _reset():
    for k in list(FILTER_KEYS) + ["f_tag"]:
        st.session_state[k] = []


def filtered():
    """Return (posts, hashtag rows) after applying the sidebar filters."""
    posts, tags = get_data()
    df = posts
    for key, col in FILTER_KEYS.items():
        chosen = st.session_state.get(key) or []
        if chosen:
            df = df[df[col].isin(chosen)]
    chosen_tags = st.session_state.get("f_tag") or []
    if chosen_tags:
        ids = tags.loc[tags["Hashtag"].isin(chosen_tags), "Post No"]
        df = df[df["Post No"].isin(ids)]
    t = tags[tags["Post No"].isin(df["Post No"])]
    if chosen_tags:
        t = t[t["Hashtag"].isin(chosen_tags)]
    return df, t


def filter_caption(df: pd.DataFrame):
    posts, _ = get_data()
    active = sum(bool(st.session_state.get(k)) for k in list(FILTER_KEYS) + ["f_tag"])
    note = f"{active} filter(s) active · " if active else ""
    st.caption(f"{note}{len(df):,} of {len(posts):,} posts in view")


@st.cache_data
def get_cube(df: pd.DataFrame) -> pd.DataFrame:
    return build_cube(df)
