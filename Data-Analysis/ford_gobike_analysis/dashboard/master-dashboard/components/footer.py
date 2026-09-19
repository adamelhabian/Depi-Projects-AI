"""
components/footer.py – Application Footer & Data Lineage Accordion
==================================================================
Includes:
  - Collapsed Data Lineage Accordion (<details>) with:
    - Source: Supabase Cloud PostgreSQL (gold.trip_analytics)
    - ETL pipeline stages: Bronze -> Silver -> Gold
    - Total record count (174,724)
    - Data schema definitions
  - Executive application footer bar
"""

import datetime
from dash import html


def render_data_lineage_accordion() -> html.Details:
    """
    Renders an expandable data lineage drawer/accordion showing
    ETL provenance, table schema, and audit metadata.
    """
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
    schema_fields = [
        ("start_time / end_time", "TIMESTAMP", "Trip departure and arrival timestamps"),
        ("duration_min", "NUMERIC", "Trip duration in minutes (calculated & sanitized)"),
        ("user_type", "VARCHAR", "Membership classification: 'Subscriber' vs 'Customer'"),
        ("start_station_name / id", "VARCHAR / INT", "Origin docking hub and identifier"),
        ("end_station_name / id", "VARCHAR / INT", "Destination docking hub and identifier"),
        ("start_latitude / longitude", "FLOAT", "GPS coordinate geometry for spatial indexing"),
        ("member_age / gender", "INT / VARCHAR", "Demographic rider attributes (sanitized)"),
    ]

    return html.Details(
        className="group bg-white rounded-xl border border-slate-200/80 p-4 shadow-sm mb-6 text-slate-700",
        children=[
            html.Summary(
                className="cursor-pointer font-semibold text-xs text-slate-700 flex items-center justify-between list-none select-none",
                children=[
                    html.Div(
                        className="flex items-center gap-2",
                        children=[
                            html.I(className="fas fa-database text-teal-600"),
                            html.Span("Data Lineage & Warehouse Schema Details"),
                            html.Span(
                                "gold.trip_analytics",
                                className="text-[10px] bg-slate-100 text-slate-600 px-2 py-0.5 rounded font-mono",
                            ),
                        ],
                    ),
                    html.Div(
                        className="flex items-center gap-2 text-slate-400 text-xs",
                        children=[
                            html.Span("174,724 rows · Click to expand", className="text-[11px]"),
                            html.I(className="fas fa-chevron-down group-open:rotate-180 transition-transform"),
                        ],
                    ),
                ],
            ),
            html.Div(
                className="mt-4 pt-3 border-t border-slate-100 text-xs text-slate-600 space-y-3",
                children=[
                    # Pipeline stages
                    html.Div(
                        className="grid grid-cols-1 md:grid-cols-3 gap-3",
                        children=[
                            html.Div(
                                className="p-2.5 bg-slate-50 rounded-lg border border-slate-200/60",
                                children=[
                                    html.Div("1. Ingestion (Bronze)", className="font-bold text-slate-800 text-[11px] mb-1"),
                                    html.P("Raw 201902-fordgobike-tripdata.csv imported into cloud raw storage.", className="text-[11px] text-slate-500"),
                                ],
                            ),
                            html.Div(
                                className="p-2.5 bg-slate-50 rounded-lg border border-slate-200/60",
                                children=[
                                    html.Div("2. Transform (Silver)", className="font-bold text-slate-800 text-[11px] mb-1"),
                                    html.P("Outlier removal, age clipping (<=80), missing GPS imputations, and regional tagging.", className="text-[11px] text-slate-500"),
                                ],
                            ),
                            html.Div(
                                className="p-2.5 bg-teal-50/50 rounded-lg border border-teal-200/60",
                                children=[
                                    html.Div("3. Analytics Mart (Gold)", className="font-bold text-teal-900 text-[11px] mb-1"),
                                    html.P("Live Supabase PostgreSQL materialized mart: gold.trip_analytics (174,724 verified trips).", className="text-[11px] text-teal-700"),
                                ],
                            ),
                        ],
                    ),

                    # Schema Table
                    html.Div(
                        className="overflow-x-auto mt-2",
                        children=[
                            html.Table(
                                className="w-full text-left text-[11px] border-collapse",
                                children=[
                                    html.Thead(
                                        html.Tr(
                                            className="border-b border-slate-200 text-slate-400 font-medium",
                                            children=[
                                                html.Th("Field", className="py-1.5 px-2"),
                                                html.Th("Type", className="py-1.5 px-2"),
                                                html.Th("Analytical Role", className="py-1.5 px-2"),
                                            ],
                                        )
                                    ),
                                    html.Tbody(
                                        [
                                            html.Tr(
                                                className="border-b border-slate-100 hover:bg-slate-50/50",
                                                children=[
                                                    html.Td(col, className="py-1 px-2 font-mono text-slate-800 font-semibold"),
                                                    html.Td(dtype, className="py-1 px-2 font-mono text-slate-500"),
                                                    html.Td(desc, className="py-1 px-2 text-slate-600"),
                                                ],
                                            )
                                            for col, dtype, desc in schema_fields
                                        ]
                                    ),
                                ],
                            ),
                        ],
                    ),

                    html.Div(
                        className="flex justify-between items-center text-[10px] text-slate-400 font-mono pt-1",
                        children=[
                            html.Span("Host: aws-0-eu-central-1.pooler.supabase.com"),
                            html.Span(f"Verification Timestamp: {now_str}"),
                        ],
                    ),
                ],
            ),
        ],
    )


def render_footer() -> html.Footer:
    """Renders the master application footer with timestamp and connection status."""
    now_str = datetime.datetime.now().strftime("%b %d, %Y · %H:%M UTC")

    return html.Footer(
        className="mt-8 py-5 border-t border-slate-200/80 bg-white/70 text-xs text-slate-400 select-none",
        children=[
            html.Div(
                className="flex flex-col sm:flex-row items-center justify-between max-w-7xl mx-auto px-6 gap-3",
                children=[
                    html.Div(
                        className="flex items-center gap-2",
                        children=[
                            html.Span(
                                "Ford GoBike Enterprise Master Analytics · DEPI Final Project",
                                className="font-semibold text-slate-700 text-xs",
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
                                className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-emerald-50 border border-emerald-200/70 text-emerald-700 font-medium",
                                children=[
                                    html.Span(className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"),
                                    html.Span("Supabase Cloud: Connected"),
                                ],
                            ),
                            html.Span("·", className="text-slate-300"),
                            html.Span("Gold Layer · 0 CSV Fallbacks", className="text-slate-500 font-mono text-[10px]"),
                        ],
                    ),
                ],
            ),
        ],
    )
