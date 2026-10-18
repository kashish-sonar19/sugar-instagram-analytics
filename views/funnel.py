"""Task 7 – Engagement funnel."""

import altair as alt
import pandas as pd
import streamlit as st

from src import theme as T
from src.data import FUNNEL_STAGES
from src.state import filtered, filter_caption

T.header("Engagement Funnel", "Task 7 · Impressions → Reach → Likes → Comments → Shares → Saves")
df, _ = filtered()
filter_caption(df)
if df.empty:
    st.stop()

tot = df[FUNNEL_STAGES].sum()
f = pd.DataFrame({"Stage": FUNNEL_STAGES, "Total": tot.values})
f["Step"] = range(1, len(f) + 1)
f["% of impressions"] = f["Total"] / f["Total"].iloc[0] * 100
f["% of reach"] = f["Total"] / f["Total"].iloc[1] * 100
f["% of previous stage"] = f["Total"] / f["Total"].shift(1) * 100
f["Label"] = f.apply(lambda r: f"{T.human(r['Total'], 2)} · {r['% of impressions']:.2f}%", axis=1)

view = st.segmented_control("Scale", ["Log scale (all stages visible)", "Linear scale (true proportions)"],
                            default="Log scale (all stages visible)") or "Log scale (all stages visible)"
log = view.startswith("Log")
LOG_FLOOR = max(1.0, 10 ** (len(str(int(f["Total"].min()))) - 2))
yscale = (alt.Scale(type="log", domain=[LOG_FLOOR, f["Total"].max() * 3]) if log
          else alt.Scale(domain=[0, f["Total"].max() * 1.12]))

cols = alt.Chart(f).mark_bar(size=70).encode(
    x=alt.X("Stage:N", sort=FUNNEL_STAGES, title=None, axis=alt.Axis(labelAngle=0, labelFontSize=13)),
    y=alt.Y("Total:Q", title="Total (log)" if log else "Total", scale=yscale),
    y2=alt.datum(LOG_FLOOR) if log else alt.datum(0),
    color=alt.Color("Step:O", scale=alt.Scale(range=["#0f3d2e", "#146b4f", "#199e70", "#3fb889", "#7fd3b2", "#a6e6cd"]),
                    legend=None),
    tooltip=["Stage", alt.Tooltip("Total:Q", format=","), alt.Tooltip("% of impressions:Q", format=".2f"),
             alt.Tooltip("% of previous stage:Q", format=".1f")])
txt = alt.Chart(f).mark_text(dy=-12, color=T.INK, fontSize=12).encode(
    x=alt.X("Stage:N", sort=FUNNEL_STAGES), y=alt.Y("Total:Q", scale=yscale),
    text="Label:N")
st.altair_chart((cols + txt).properties(height=380, width="container",
                                       title="Step-down funnel (value · % of impressions)"), theme=None)

conv = f.dropna(subset=["% of previous stage"]).copy()
conv["Transition"] = [f"{a} → {b}" for a, b in zip(FUNNEL_STAGES[:-1], FUNNEL_STAGES[1:])]
cbar = alt.Chart(conv).mark_bar(color="#9085e9").encode(
    y=alt.Y("Transition:N", sort=conv["Transition"].tolist(), title=None),
    x=alt.X("% of previous stage:Q", title="% of previous stage"),
    tooltip=["Transition", alt.Tooltip("% of previous stage:Q", format=".1f")])
ctxt = alt.Chart(conv).mark_text(align="left", dx=5, color=T.INK).encode(
    y=alt.Y("Transition:N", sort=conv["Transition"].tolist()), x="% of previous stage:Q",
    text=alt.Text("% of previous stage:Q", format=".1f"))
st.altair_chart((cbar + ctxt).properties(height=240, width="container", title="Stage-to-stage conversion"),
                theme=None)

st.dataframe(f[["Stage", "Total", "% of impressions", "% of reach", "% of previous stage"]].round(2),
             hide_index=True)

st.subheader("Follower path")
g = pd.DataFrame({"Stage": ["Reach", "Profile Visits", "Follows"],
                  "Total": [df["Reach"].sum(), df["Profile Visits"].sum(), df["Follows"].sum()]})
c1, c2, c3 = st.columns(3)
c1.metric("Reach → profile visit", f"{g.Total[1] / g.Total[0]:.2%}")
c2.metric("Profile visit → follow", f"{g.Total[2] / g.Total[1]:.1%}")
c3.metric("Reach → follow", f"{g.Total[2] / g.Total[0]:.2%}")

T.takeaway(f"The sharpest drop is right after reach: only <b>{f.loc[2, '% of reach']:.1f}%</b> of reached users like, "
           f"and comments, shares and saves are each under 2% of reach. Saves ({T.human(tot['Saves'])}) slightly exceed "
           f"shares ({T.human(tot['Shares'])}), so content is being bookmarked more than passed on. "
           f"Profile visitors convert well ({g.Total[2] / g.Total[1]:.0%} follow) — the opportunity is getting more people to the profile.")
