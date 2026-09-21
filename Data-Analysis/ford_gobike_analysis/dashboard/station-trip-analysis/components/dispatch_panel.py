"""
components/dispatch_panel.py – Prescriptive Fleet Rebalancing Dispatch Panel
=============================================================================
Rebuilt as a clean grid of Tailwind-only cards to eliminate CSS collision
between the custom dispatch-* classes and the parent master dashboard styles.

Card anatomy (per pair):
  ┌────────────────────────────────────────────────────────────┐
  │  # Pair 1 · San Francisco          📍 0.72 km apart        │
  │                                                            │
  │  [SURPLUS SOURCE]  ────→ Transfer ~42 bikes ────→  [DEFICIT TARGET]  │
  │  19th St BART         🚲                          Powell St BART  │
  │  +159 net arrivals                                -88 net depart. │
  └────────────────────────────────────────────────────────────┘
"""

from __future__ import annotations

from dash import html


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _station_node(
    label: str,          # "SURPLUS SOURCE" | "DEFICIT TARGET"
    station_name: str,
    stat_text: str,      # "+159 net arrivals" | "-88 net departures"
    is_surplus: bool,
) -> html.Div:
    """One station box (source or target) inside the flow row."""
    if is_surplus:
        border   = "border-l-4 border-l-emerald-500"
        label_cl = "text-emerald-600 text-[9px] font-black uppercase tracking-widest mb-1"
        stat_cl  = "text-emerald-700 text-[11px] font-semibold mt-1"
    else:
        border   = "border-l-4 border-l-rose-500"
        label_cl = "text-rose-600 text-[9px] font-black uppercase tracking-widest mb-1"
        stat_cl  = "text-rose-700 text-[11px] font-semibold mt-1"

    # Smart truncation: keep first 30 chars and add ellipsis if longer
    display_name = station_name if len(station_name) <= 30 else station_name[:28] + "…"

    return html.Div(
        className=f"flex-1 bg-white rounded-xl p-3 shadow-sm {border}",
        style={"minWidth": "0"},
        title=station_name,          # native tooltip shows full name on hover
        children=[
            html.Span(label, className=label_cl),
            html.Div(display_name, className="text-slate-800 text-[12px] font-bold leading-snug"),
            html.Div(stat_text, className=stat_cl),
        ],
    )


def _transfer_arrow(qty: int) -> html.Div:
    """Center column: bike count pill + arrow."""
    return html.Div(
        className="flex flex-col items-center gap-1 px-2 shrink-0",
        children=[
            html.Span(
                f"~{qty} bikes",
                className="bg-emerald-50 border border-emerald-200 text-emerald-700 text-[10px] font-bold px-3 py-1 rounded-full whitespace-nowrap",
            ),
            html.Div(
                className="text-emerald-500 text-lg font-bold leading-none",
                children="→",
            ),
        ],
    )


# ---------------------------------------------------------------------------
# public render function
# ---------------------------------------------------------------------------

def render_dispatch_panel(pairs: list[dict] | None = None) -> html.Div:
    """
    Render the Smart Fleet Rebalancing dispatch panel.

    Parameters
    ----------
    pairs : list[dict]
        Each dict must contain the keys produced by compute_smart_dispatch_pairs().
    """
    # ── Panel header ────────────────────────────────────────────────────────
    header = html.Div(
        className="mb-5",
        children=[
            html.Div(
                className="flex items-center gap-2 mb-2",
                children=[
                    html.Span(
                        "PRESCRIPTIVE DISPATCH",
                        className="bg-teal-100 text-teal-800 text-[10px] font-black uppercase tracking-widest px-2.5 py-0.5 rounded",
                    ),
                    html.Span(
                        "Automated Spatial Match · Haversine Algorithm",
                        className="text-xs text-slate-400 font-medium",
                    ),
                ],
            ),
            html.H3(
                "Smart Fleet Rebalancing Recommendations",
                className="text-base sm:text-lg font-extrabold text-slate-900 tracking-tight",
            ),
            html.P(
                "Each pair matches the nearest high-deficit station with its "
                "highest-surplus neighbour in the same metro cluster.",
                className="text-xs text-slate-500 mt-0.5 leading-relaxed",
            ),
        ],
    )

    # ── Empty / balanced state ───────────────────────────────────────────────
    if not pairs:
        content = html.Div(
            className="text-center py-10 bg-slate-50 rounded-xl border border-dashed border-slate-200",
            children=[
                html.Div("✅", className="text-3xl mb-2"),
                html.P(
                    "Network is well balanced — no severe deficit–surplus pairs "
                    "exceed threshold in the current filter selection.",
                    className="text-slate-400 text-sm max-w-sm mx-auto",
                ),
            ],
        )
        return html.Div(
            className="bg-white rounded-2xl border border-slate-200 shadow-sm p-5 mb-8",
            children=[header, content],
        )

    # ── Build one card per pair ──────────────────────────────────────────────
    cards = []
    for idx, p in enumerate(pairs):
        surplus_stn   = p["surplus_station"]
        deficit_stn   = p["deficit_station"]
        transfer_qty  = int(p["recommended_transfer"])
        dist_km       = float(p["distance_km"])
        region        = p["region"]
        surplus_amt   = int(p["surplus_amount"])
        deficit_amt   = int(p["deficit_amount"])

        card = html.Div(
            className="bg-slate-50 border border-slate-200 rounded-2xl p-4 hover:border-emerald-300 hover:shadow-sm transition-all duration-200",
            children=[
                # ── Card header: rank + region + distance ──────────────────
                html.Div(
                    className="flex items-center justify-between mb-3",
                    children=[
                        html.Div(
                            className="flex items-center gap-2",
                            children=[
                                html.Span(
                                    f"#{idx + 1}",
                                    className="w-6 h-6 rounded-full bg-slate-800 text-white text-[11px] font-black flex items-center justify-center shrink-0",
                                ),
                                html.Span(
                                    region,
                                    className="text-slate-700 text-[12px] font-bold",
                                ),
                            ],
                        ),
                        html.Span(
                            f"📍 {dist_km:.2f} km apart",
                            className="bg-lime-50 border border-lime-200 text-lime-800 text-[11px] font-semibold px-2.5 py-0.5 rounded-full",
                        ),
                    ],
                ),

                # ── Flow row: Source → Arrow → Target ──────────────────────
                html.Div(
                    className="flex items-center gap-2",
                    children=[
                        _station_node(
                            label="SURPLUS SOURCE",
                            station_name=surplus_stn,
                            stat_text=f"+{surplus_amt:,} net arrivals",
                            is_surplus=True,
                        ),
                        _transfer_arrow(transfer_qty),
                        _station_node(
                            label="DEFICIT TARGET",
                            station_name=deficit_stn,
                            stat_text=f"−{deficit_amt:,} net departures",
                            is_surplus=False,
                        ),
                    ],
                ),

                # ── Action line ─────────────────────────────────────────────
                html.Div(
                    className="mt-3 pt-3 border-t border-slate-200/80 flex items-center gap-1.5",
                    children=[
                        html.Span("🚛", className="text-sm"),
                        html.Span(
                            f"Dispatch truck to transfer approximately {transfer_qty} bikes "
                            f"from {surplus_stn[:25]}{'…' if len(surplus_stn) > 25 else ''} "
                            f"→ {deficit_stn[:25]}{'…' if len(deficit_stn) > 25 else ''}.",
                            className="text-[11px] text-slate-500 leading-relaxed",
                        ),
                    ],
                ),
            ],
        )
        cards.append(card)

    content = html.Div(
        className="flex flex-col gap-3",
        children=cards,
    )

    return html.Div(
        className="bg-white rounded-2xl border border-slate-200 shadow-sm p-5 mb-8",
        children=[header, content],
    )
