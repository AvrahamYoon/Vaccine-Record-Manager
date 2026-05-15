# Modern color palette (Tailwind-inspired)
COLORS = [
    "#3b82f6",  # blue-500
    "#10b981",  # emerald-500
    "#f59e0b",  # amber-500
    "#8b5cf6",  # violet-500
    "#ec4899",  # pink-500
    "#06b6d4",  # cyan-500
]


def apply_chart_style(fig, **kwargs):
    """
    Applies a consistent, modern style to Plotly figures.
    """
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=40, b=40, l=40, r=20),
        font=dict(
            family="'Inter', -apple-system, BlinkMacSystemFont, sans-serif",
            size=13,
            color="#475569",
        ),
        hoverlabel=dict(
            bgcolor="#ffffff",
            font_size=13,
            font_family="'Inter', sans-serif",
            bordercolor="#e2e8f0",
        ),
        hovermode="closest",
        # Entry animation
        transition_duration=800,
        transition_easing="cubic-in-out",
        **kwargs,
    )

    fig.update_xaxes(
        showgrid=True,
        gridcolor="#f1f5f9",
        linecolor="#e2e8f0",
        tickfont=dict(color="#64748b"),
        zeroline=False,
    )
    fig.update_yaxes(
        showgrid=True,
        gridcolor="#f1f5f9",
        linecolor="#e2e8f0",
        tickfont=dict(color="#64748b"),
        zeroline=False,
    )

    # If it's a bar chart, add some rounding to corners
    if fig.data and fig.data[0].type == "bar":
        fig.update_traces(marker_line_width=0, opacity=0.9)

    return fig
