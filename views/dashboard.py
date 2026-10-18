"""Task 9 – Combined interactive dashboard (Altair cross-filtering)."""

import altair as alt
import streamlit as st

from src import theme as T
from src.data import DAY_ORDER, FUNNEL_STAGES
from src.state import filtered, filter_caption, get_cube

T.header("Instagram Insights Report — Sugar Cosmetics",
         "Click a bar in <b>Format</b>, <b>Day</b> or <b>Campaign</b> to filter every other chart. "
         "Shift+click to pick several · double-click a chart's empty area to clear. "
         "Sidebar filters apply first.")

df, tags = filtered()
filter_caption(df)
if df.empty:
    st.warning("No posts match the sidebar filters.")
    st.stop()

cube = get_cube(df.drop(columns=["Tag List"]))
tag_cube = (tags.assign(Day=tags["Day"].astype(str))
            .groupby(["Hashtag", "Post Type", "Day", "Campaign Type"], observed=True)
            .agg(Reach=("Reach", "sum"), Engagements=("Engagements", "sum"), Posts=("Post No", "size"))
            .reset_index())

sel_fmt = alt.selection_point(fields=["Post Type"], name="fmt")
sel_day = alt.selection_point(fields=["Day"], name="day")
sel_camp = alt.selection_point(fields=["Campaign Type"], name="camp")
ALL = [sel_fmt, sel_day, sel_camp]


def filt(chart, skip=None):
    for s in ALL:
        if s is not skip:
            chart = chart.transform_filter(s)
    return chart


base = alt.Chart(cube)

# ---- KPI tiles ---------------------------------------------------------------
def tile(title, agg_field, fmt, calc=None, suffix=""):
    key = "k_" + (agg_field or "er").lower()
    c = filt(base)
    if calc:
        c = (c.transform_aggregate(e_k="sum(Engagements)", r_k="sum(Reach)")
             .transform_calculate(**{key: calc.replace("datum.e", "datum.e_k").replace("datum.r", "datum.r_k")}))
    else:
        c = c.transform_aggregate(**{key: f"sum({agg_field})"})
    c = c.transform_calculate(label=f"format(datum.{key}, '{fmt}') + '{suffix}'")
    value = c.mark_text(fontSize=30, fontWeight=700, color=T.INK).encode(text="label:N")
    return value.properties(width=170, height=56, title=alt.Title(title, fontSize=12, color=T.INK_2,
                                                                  fontWeight=400, anchor="middle"))


kpis = alt.hconcat(
    tile("TOTAL POSTS", "Posts", ","),
    tile("TOTAL LIKES", "Likes", ".4~s"),
    tile("TOTAL COMMENTS", "Comments", ".4~s"),
    tile("TOTAL REACH", "Reach", ".4~s"),
    tile("ENGAGEMENT RATE", None, ".2f", calc="datum.e / datum.r * 100", suffix="%"),
    spacing=40,
)

# ---- Monthly posts -------------------------------------------------------------
monthly = filt(base).mark_line(point=alt.OverlayMarkDef(color=T.ACCENT, size=60), color=T.ACCENT).encode(
    x=alt.X("utcyearmonth(Month):T", title=None, axis=alt.Axis(format="%b %y", labelAngle=0)),
    y=alt.Y("sum(Posts):Q", title="Posts"),
    tooltip=[alt.Tooltip("utcyearmonth(Month):T", title="Month", format="%b %Y"),
             alt.Tooltip("sum(Posts):Q", title="Posts", format=",")],
).properties(width=560, height=220, title="Posts per month")

# ---- Funnel --------------------------------------------------------------------
funnel = (filt(base)
          .transform_aggregate(**{s: f"sum({s})" for s in FUNNEL_STAGES})
          .transform_fold(FUNNEL_STAGES, as_=["Stage", "Total"])
          .transform_joinaggregate(Top="max(Total)")
          .transform_calculate(Pct="datum.Total / datum.Top * 100",
                               label="format(datum.Pct, '.2f') + '%'"))
log_x = alt.X("Pct:Q", scale=alt.Scale(type="log", domain=[0.3, 250]), axis=None)
f_bar = funnel.mark_bar(color=T.ACCENT).encode(
    y=alt.Y("Stage:N", sort=FUNNEL_STAGES, title=None), x=log_x, x2=alt.datum(0.3),
    tooltip=[alt.Tooltip("Stage:N"), alt.Tooltip("Total:Q", format=","),
             alt.Tooltip("Pct:Q", title="% of impressions", format=".2f")],
)
f_txt = funnel.mark_text(align="left", dx=6, color=T.INK).encode(
    y=alt.Y("Stage:N", sort=FUNNEL_STAGES), x=log_x, text="label:N")
funnel_chart = (f_bar + f_txt).properties(width=300, height=220,
                                          title="Funnel · % of impressions (log scale)")


# ---- Selectable bar charts -----------------------------------------------------
def er_bars(field, sel, sort, width, horizontal=False, color=None):
    c = (filt(base, skip=sel)
         .transform_aggregate(e="sum(Engagements)", r="sum(Reach)", n="sum(Posts)", groupby=[field])
         .transform_calculate(ER="datum.e / datum.r * 100"))
    col = alt.condition(sel, color if color is not None else alt.value(T.ACCENT), alt.value(T.MUTED))
    pos, val = (alt.Y, alt.X) if horizontal else (alt.X, alt.Y)
    enc = dict(
        tooltip=[alt.Tooltip(f"{field}:N"), alt.Tooltip("ER:Q", title="ER %", format=".2f"),
                 alt.Tooltip("n:Q", title="Posts", format=",")],
    )
    bar_pos = pos(f"{field}:N", sort=sort, title=None,
                  axis=alt.Axis(labelAngle=0) if not horizontal else alt.Axis())
    bar_val = val("ER:Q", title="Engagement rate %", scale=alt.Scale(domain=[0, 22]))
    bars = c.mark_bar().encode(bar_pos, bar_val, color=col, **enc).add_params(sel)
    txt = c.mark_text(dx=18 if horizontal else 0, dy=0 if horizontal else -8, color=T.INK).encode(
        bar_pos, bar_val, text=alt.Text("ER:Q", format=".2f"))
    return bars + txt, width


fmt_chart, _ = er_bars("Post Type", sel_fmt, list(T.FORMAT_COLORS), 300,
                       color=alt.Color("Post Type:N", scale=T.FORMAT_SCALE, legend=None))
day_chart, _ = er_bars("Day", sel_day, DAY_ORDER, 380)
camp_chart, _ = er_bars("Campaign Type", sel_camp, "-x", 200, horizontal=True)

fmt_chart = fmt_chart.properties(width=250, height=220, title="Format · ER %")
day_chart = day_chart.properties(width=330, height=220, title="Day of week · ER %")
camp_chart = camp_chart.properties(width=200, height=220, title="Campaign · ER %")

# ---- Hashtags (filtered by all selections) ------------------------------------
tag_chart = (filt(alt.Chart(tag_cube))
             .transform_aggregate(e="sum(Engagements)", r="sum(Reach)", n="sum(Posts)", groupby=["Hashtag"])
             .transform_calculate(ER="datum.e / datum.r * 100"))
tag_bars = tag_chart.mark_bar(color=T.ACCENT).encode(
    y=alt.Y("Hashtag:N", sort="-x", title=None),
    x=alt.X("ER:Q", title="Engagement rate %", scale=alt.Scale(domain=[0, 22])),
    tooltip=[alt.Tooltip("Hashtag:N"), alt.Tooltip("ER:Q", format=".2f"), alt.Tooltip("n:Q", title="Posts", format=",")])
tag_txt = tag_chart.mark_text(align="left", dx=4, color=T.INK).encode(
    y=alt.Y("Hashtag:N", sort="-x"), x="ER:Q", text=alt.Text("ER:Q", format=".2f"))
tags_final = (tag_bars + tag_txt).properties(width=380, height=200, title="Hashtag · ER %")

src_chart = (filt(base)
             .transform_aggregate(r="sum(Reach)", n="sum(Posts)", groupby=["Engagement Source"])
             .transform_calculate(avg="datum.r / datum.n"))
src_bars = src_chart.mark_bar(color="#9085e9").encode(
    x=alt.X("Engagement Source:N", title=None, axis=alt.Axis(labelAngle=0)),
    y=alt.Y("avg:Q", title="Avg reach per post"),
    tooltip=[alt.Tooltip("Engagement Source:N"), alt.Tooltip("avg:Q", format=",.0f"), alt.Tooltip("n:Q", format=",")])
src_txt = src_chart.mark_text(dy=-8, color=T.INK).encode(
    x="Engagement Source:N", y="avg:Q", text=alt.Text("avg:Q", format=",.0f"))
src_final = (src_bars + src_txt).properties(width=470, height=200, title="Avg reach per post by source")

dashboard = alt.vconcat(
    kpis,
    alt.hconcat(monthly, funnel_chart, spacing=40),
    alt.hconcat(fmt_chart, day_chart, camp_chart, spacing=30),
    alt.hconcat(tags_final, src_final, spacing=40),
    spacing=34,
).resolve_scale(color="independent")

st.altair_chart(dashboard, theme=None, width="content")

st.subheader("Top posts (sidebar filters)")
c1, c2 = st.columns(2)
cols = ["Post Name", "Likes", "Reach", "ER %"]
c1.markdown("**By likes**")
c1.dataframe(df.nlargest(10, "Likes")[cols], hide_index=True,
             column_config={"ER %": st.column_config.NumberColumn(format="%.2f")})
c2.markdown("**By engagement rate**")
c2.dataframe(df.nlargest(10, "ER %")[cols], hide_index=True,
             column_config={"ER %": st.column_config.NumberColumn(format="%.2f")})
