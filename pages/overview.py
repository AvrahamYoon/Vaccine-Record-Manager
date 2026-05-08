import pandas as pd
import plotly.express as px
import streamlit as st

from core.charts import COLORS, apply_chart_style


def render_overview_page(df: pd.DataFrame, T: dict):
    st.title(T["pages"][0])

    total = len(df)
    kinds = df["_display_name"].nunique()
    last_dt = pd.to_datetime(df["date"], errors="coerce").max()
    last_date_str = last_dt.strftime("%Y-%m-%d") if pd.notna(last_dt) else "—"
    left = int((df["arm"] == "L").sum())
    right = int((df["arm"] == "R").sum())

    cols = st.columns(5)
    for col, label, value in zip(
        cols, [T["total"], T["kinds"], T["last_date"], T["left_arm"], T["right_arm"]], [total, kinds, last_date_str, left, right]
    ):
        col.markdown(
            f'<div class="stat-card"><div class="stat-label">{label}</div><div class="stat-value">{value}</div></div>',
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    df_dated = df.copy()
    df_dated["year"] = pd.to_datetime(df_dated["date"], errors="coerce").dt.year

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown(f"#### {T['yearly_chart']}")
        yearly = df_dated.groupby("year").size().reset_index(name=T["count"])
        yearly = yearly.dropna(subset=["year"])
        yearly["year"] = yearly["year"].astype(int).astype(str)
        fig = px.bar(yearly, x="year", y=T["count"], text=T["count"], color_discrete_sequence=[COLORS[0]])
        apply_chart_style(fig, xaxis_title=T["year"], yaxis_title=T["count"])
        fig.update_traces(marker_line_width=0, textposition="outside")
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        st.markdown(f"#### {T['arm_chart']}")
        arm_df = df[df["arm"].isin(["L", "R"])]["arm"].value_counts().reset_index()
        arm_df.columns = ["arm", T["count"]]
        arm_df["arm"] = arm_df["arm"].map({"L": T["left_arm"], "R": T["right_arm"]})
        fig2 = px.pie(arm_df, names="arm", values=T["count"], hole=0.45, color_discrete_sequence=[COLORS[0], COLORS[1]])
        apply_chart_style(fig2)
        fig2.update_traces(textposition="outside", textinfo="percent+label")
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("---")
    st.markdown(f"#### {T['timeline']}")
    df_r = df.copy()
    df_r["date_parsed"] = pd.to_datetime(df_r["date"], errors="coerce")
    timeline = df_r.dropna(subset=["date_parsed"]).sort_values("date_parsed")
    fig_tl = px.scatter(
        timeline,
        x="date_parsed",
        y="_display_name",
        color="_display_name",
        hover_data=["dose", "provider", "arm"],
        labels={"date_parsed": T["col_date"][:4], "_display_name": T["col_name"]},
        color_discrete_sequence=px.colors.qualitative.Pastel,
    )
    fig_tl.update_traces(marker=dict(size=11, opacity=0.8, line=dict(width=1, color="#ffffff")))
    apply_chart_style(fig_tl, showlegend=False, height=360)
    st.plotly_chart(fig_tl, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"#### {T['vac_count']}")
        vc = df_r["_display_name"].value_counts().reset_index()
        vc.columns = [T["col_name"], T["count"]]
        fig_vc = px.bar(vc, x=T["count"], y=T["col_name"], orientation="h", color_discrete_sequence=[COLORS[0]])
        apply_chart_style(fig_vc)
        fig_vc.update_layout(yaxis={"categoryorder": "total ascending"})
        fig_vc.update_traces(marker_line_width=0)
        st.plotly_chart(fig_vc, use_container_width=True)

    with col2:
        st.markdown(f"#### {T['provider_stat']}")
        pc = df_r["provider"].value_counts().reset_index()
        pc.columns = [T["col_prov"], T["count"]]
        fig_pc = px.bar(pc, x=T["count"], y=T["col_prov"], orientation="h", color_discrete_sequence=[COLORS[2]])
        apply_chart_style(fig_pc)
        fig_pc.update_layout(yaxis={"categoryorder": "total ascending"})
        fig_pc.update_traces(marker_line_width=0)
        st.plotly_chart(fig_pc, use_container_width=True)
