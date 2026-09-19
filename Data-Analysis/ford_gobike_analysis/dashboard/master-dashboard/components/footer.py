"""
components/footer.py – Application Footer
=========================================
"""

from __future__ import annotations

from dash import html


def render_footer() -> html.Footer:
    """Renders the master application footer."""
    return html.Footer(
        className="mt-12 py-6 border-t border-slate-200/80 text-center text-xs text-slate-400 select-none",
        children=[
            html.Div(
                className="flex flex-col sm:flex-row items-center justify-between max-w-7xl mx-auto px-4 gap-2",
                children=[
                    html.Span(
                        "Ford GoBike Enterprise Master BI Platform · DEPI Final Project",
                        className="font-medium text-slate-500",
                    ),
                    html.Div(
                        className="flex items-center gap-4 text-[11px]",
                        children=[
                            html.Span("Direct Supabase Cloud ETL"),
                            html.Span("·"),
                            html.Span("Multi-Module Distributed Architecture"),
                        ],
                    ),
                ],
            ),
        ],
    )
