COLORS = ["#6ea8fe", "#f4a261", "#6bcb77", "#ffd166", "#a78bfa", "#f472b6"]


def apply_chart_style(fig, **kwargs):
    fig.update_layout(
        plot_bgcolor="#ffffff",
        paper_bgcolor="#ffffff",
        margin=dict(t=8, b=8, l=8, r=8),
        font=dict(family="system-ui, -apple-system, sans-serif", size=12, color="#4b5563"),
        **kwargs,
    )
    fig.update_xaxes(showgrid=True, gridcolor="#f3f4f6", zeroline=False)
    fig.update_yaxes(showgrid=True, gridcolor="#f3f4f6", zeroline=False)
    return fig
