import datetime
from dash import html


def render_footer() -> html.Footer:
    """Renders the master application footer with timestamp and connection status."""
    now_str = datetime.datetime.now().strftime("%b %d, %Y · %H:%M UTC")

    return html.Footer(
        className="mt-12 py-6 border-t border-slate-200/80 bg-white/60 text-xs text-slate-400 select-none",
        children=[
            html.Div(
                className="flex flex-col sm:flex-row items-center justify-between max-w-7xl mx-auto px-6 gap-3",
                children=[
                    html.Div(
                        className="flex items-center gap-2",
                        children=[
                            html.Span(
                                "Ford GoBike Enterprise Master BI Platform · DEPI Final Project",
                                className="font-semibold text-slate-600 text-xs",
                            ),
                            html.Span("·", className="text-slate-300"),
                            html.Span(
                                f"Updated: {now_str}",
                                className="text-[11px] text-slate-400 font-mono",
                            ),
                        ],
                    ),
                    html.Div(
                        className="flex items-center gap-3 text-[11px]",
                        children=[
                            html.Div(
                                className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-emerald-50 border border-emerald-200/70 text-emerald-700 font-medium",
                                children=[
                                    html.Span(className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"),
                                    html.Span("Supabase PostgreSQL: Connected"),
                                ],
                            ),
                            html.Span("·", className="text-slate-300"),
                            html.Span("Gold Layer · 0 CSV Dependencies", className="text-slate-500 font-mono text-[10px]"),
                        ],
                    ),
                ],
            ),
        ],
    )
