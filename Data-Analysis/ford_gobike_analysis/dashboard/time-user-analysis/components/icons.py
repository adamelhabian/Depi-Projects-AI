"""
components/icons.py – SVG Icon Library for Dash UI
===================================================
Provides crisp, standalone SVG icons via self-contained data URIs.
Zero external CDN dependencies, 100% Dash compatible (no dash.html.Svg required).
"""
import urllib.parse
from dash import html


def _svg_to_img(svg_str: str, class_name: str = "w-4 h-4 inline-block") -> html.Img:
    data_uri = "data:image/svg+xml;utf8," + urllib.parse.quote(svg_str.strip())
    return html.Img(src=data_uri, className=class_name, alt="", role="presentation")


def icon_download(class_name: str = "w-3.5 h-3.5 inline-block mr-1.5") -> html.Img:
    """Download tray icon for Export CSV button."""
    svg = (
        "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' "
        "stroke='white' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'>"
        "<path d='M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4'></path>"
        "<polyline points='7 10 12 15 17 10'></polyline>"
        "<line x1='12' y1='15' x2='12' y2='3'></line>"
        "</svg>"
    )
    return _svg_to_img(svg, class_name)


def icon_crosshair(class_name: str = "w-4 h-4 inline-block mr-2") -> html.Img:
    """Focus crosshairs icon for Station Inspector button."""
    svg = (
        "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' "
        "stroke='white' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'>"
        "<circle cx='12' cy='12' r='8'></circle>"
        "<line x1='22' y1='12' x2='18' y2='12'></line>"
        "<line x1='6' y1='12' x2='2' y2='12'></line>"
        "<line x1='12' y1='6' x2='12' y2='2'></line>"
        "<line x1='12' y1='22' x2='12' y2='18'></line>"
        "</svg>"
    )
    return _svg_to_img(svg, class_name)


def icon_close(class_name: str = "w-4 h-4 inline-block") -> html.Img:
    """Close cross icon for drawer header."""
    svg = (
        "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' "
        "stroke='%2364748B' stroke-width='2.5' stroke-linecap='round' stroke-linejoin='round'>"
        "<line x1='18' y1='6' x2='6' y2='18'></line>"
        "<line x1='6' y1='6' x2='18' y2='18'></line>"
        "</svg>"
    )
    return _svg_to_img(svg, class_name)


def icon_check_circle(class_name: str = "w-8 h-8 mx-auto mb-2 block") -> html.Img:
    """Emerald checkmark circle for balanced network state."""
    svg = (
        "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' "
        "stroke='%2310B981' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'>"
        "<circle cx='12' cy='12' r='10'></circle>"
        "<polyline points='8 12 11 15 16 9'></polyline>"
        "</svg>"
    )
    return _svg_to_img(svg, class_name)


def icon_pin(class_name: str = "w-3.5 h-3.5 inline-block mr-1") -> html.Img:
    """Location pin icon for dispatch distance badge."""
    svg = (
        "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='%2364748B' "
        "stroke='%2364748B' stroke-width='1.5' stroke-linecap='round' stroke-linejoin='round'>"
        "<path d='M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z'></path>"
        "<circle cx='12' cy='10' r='3' fill='white'></circle>"
        "</svg>"
    )
    return _svg_to_img(svg, class_name)


def icon_arrow_right(class_name: str = "w-4 h-4 mx-auto block") -> html.Img:
    """Directional arrow for rebalancing dispatch card."""
    svg = (
        "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' "
        "stroke='%2394A3B8' stroke-width='2.5' stroke-linecap='round' stroke-linejoin='round'>"
        "<line x1='5' y1='12' x2='19' y2='12'></line>"
        "<polyline points='12 5 19 12 12 19'></polyline>"
        "</svg>"
    )
    return _svg_to_img(svg, class_name)
