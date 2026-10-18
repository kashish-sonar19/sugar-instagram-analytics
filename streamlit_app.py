"""
Sugar Cosmetics – Instagram Content Performance Dashboard
Author: Kashish Haresh Sonar

Run:  streamlit run streamlit_app.py
"""

import streamlit as st

from src import theme
from src.state import sidebar_filters

st.set_page_config(page_title="Sugar Instagram Dashboard", page_icon="💄", layout="wide")
theme.register()
theme.inject_css()

pages = {
    "Summary": [
        st.Page("views/dashboard.py", title="Interactive Dashboard", icon="🧭", default=True),
        st.Page("views/overview.py", title="KPIs & Posting Trend", icon="📌"),
    ],
    "Content analysis": [
        st.Page("views/top_posts.py", title="Top Posts", icon="🏆"),
        st.Page("views/formats.py", title="Post Formats", icon="🎞️"),
        st.Page("views/timing.py", title="Best Days to Post", icon="🗓️"),
        st.Page("views/funnel.py", title="Engagement Funnel", icon="🔻"),
        st.Page("views/hashtags.py", title="Hashtags", icon="#️⃣"),
    ],
    "Strategy": [
        st.Page("views/strategy.py", title="Recommendations", icon="🎯"),
        st.Page("views/data_quality.py", title="Data & Method", icon="🧹"),
    ],
}

nav = st.navigation(pages)
sidebar_filters()
st.sidebar.divider()
st.sidebar.caption("Built by **Kashish Haresh Sonar** · Labmentrix")
nav.run()
