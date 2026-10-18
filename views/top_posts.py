"""Task 3 (Top 10 by likes) + Task 4 (Top 10 by engagement rate)."""

import altair as alt
import streamlit as st

from src import theme as T
from src.state import filtered, filter_caption

T.header("Top Posts", "Task 3 · most-liked posts  ·  Task 4 · highest engagement rate (the hidden gems)")
df, _ = filtered()
filter_caption(df)
if len(df) < 10:
    st.warning("Need at least 10 posts — relax the filters.")
    st.stop()
st.caption("The dataset has no caption column, so each post is named: #ID Format – Campaign (date).")


def lollipop(top, metric, fmt, title):
    order = top["Post Name"].tolist()
    base = alt.Chart(top).encode(y=alt.Y("Post Name:N", sort=order, title=None,
                                         axis=alt.Axis(labelLimit=320)))
    rule = base.mark_rule(color="#5a5a55", strokeWidth=2).encode(x=alt.X(f"{metric}:Q", title=metric,
                                                                      scale=alt.Scale(zero=True)), x2=alt.value(0))
    dot = base.mark_circle(size=170, opacity=1).encode(
        x=f"{metric}:Q", color=alt.Color("Post Type:N", scale=T.FORMAT_SCALE, title="Format"),
        tooltip=["Post Name", "Hashtags", alt.Tooltip("Likes:Q", format=","), alt.Tooltip("Reach:Q", format=","),
                 alt.Tooltip("ER %:Q", format=".2f"), alt.Tooltip("Saves:Q", format=","),
                 alt.Tooltip("Shares:Q", format=",")])
    txt = base.mark_text(align="left", dx=12, color=T.INK).encode(x=f"{metric}:Q", text=alt.Text(f"{metric}:Q", format=fmt))
    return (rule + dot + txt).properties(height=380, width="container", title=title)


cols = ["Post Name", "Post Type", "Campaign Type", "Hashtags", "Likes", "Comments", "Saves", "Shares", "Reach", "ER %"]

# ---------------- Task 3 ----------------
st.subheader("3 · Top 10 posts by likes")
top_likes = df.nlargest(10, "Likes")
st.altair_chart(lollipop(top_likes, "Likes", ",", "Most-liked posts"), theme=None)
st.dataframe(top_likes[cols], hide_index=True, column_config={
    "Likes": st.column_config.ProgressColumn(format="%d", min_value=0, max_value=int(df["Likes"].max())),
    "ER %": st.column_config.NumberColumn(format="%.2f")})
T.takeaway(f"Most-liked posts are driven by <b>reach</b>: they average {top_likes['Reach'].mean():,.0f} reach vs "
           f"{df['Reach'].mean():,.0f} for a typical post, but their ER ({top_likes['ER %'].mean():.1f}%) is not exceptional.")

# ---------------- Task 4 ----------------
st.subheader("4 · Top 10 posts by engagement rate")
floor = st.select_slider("Ignore posts with reach below", options=[0, 1000, 2500, 5000, 10000, 20000], value=0)
pool = df[df["Reach"] >= floor]
top_er = pool.nlargest(10, "ER %")
st.altair_chart(lollipop(top_er, "ER %", ".2f", "Highest engagement rate"), theme=None)

median_likes = df["Likes"].median()
show = top_er[cols].copy()
show["Hidden gem"] = (show["Likes"] < median_likes) | (show["Reach"] < df["Reach"].median())
st.dataframe(show, hide_index=True, column_config={
    "ER %": st.column_config.ProgressColumn(format="%.2f", min_value=0, max_value=float(df["ER %"].max())),
    "Hidden gem": st.column_config.CheckboxColumn(help="Below-median likes or reach, but top-10 ER")})

scatter = alt.Chart(df.sample(min(len(df), 3000), random_state=7)).mark_circle(size=40, opacity=0.5).encode(
    x=alt.X("Likes:Q", title="Likes"), y=alt.Y("ER %:Q", title="Engagement rate %"),
    color=alt.Color("Post Type:N", scale=T.FORMAT_SCALE, title="Format"),
    tooltip=["Post Name", alt.Tooltip("Likes:Q", format=","), alt.Tooltip("ER %:Q", format=".2f")],
).properties(height=320, width="container", title="Likes vs engagement rate (3,000-post sample)")
st.altair_chart(scatter, theme=None)

gems = int(show["Hidden gem"].sum())
T.takeaway(f"<b>{gems} of the top 10</b> ER posts had below-median likes or reach — small audiences that engaged "
           "unusually well. These are the best posts to boost or repurpose. Overlap between the two top-10 lists: "
           f"<b>{len(set(top_likes['Post No']) & set(top_er['Post No']))}</b> post(s).")
