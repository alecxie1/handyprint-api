"""
Step 4 — Fabric.js Canvas Assembly

Builds a layered Fabric.js JSON canvas for a given image + format,
compresses it (gzip → base64), and POSTs to the yft-design backend
via PUT /admin/template/{id}/pages.

Returns the editor URL: {YFT_FRONTEND_URL}/?template_id={id}
"""

import base64
import gzip
import json
import os
import uuid
from pathlib import Path

import requests

from config import FORMATS, TEMPLATE_IDS, YFT_BACKEND_URL

# Frontend URL (the yft-design editor)
YFT_FRONTEND_URL = os.getenv("YFT_FRONTEND_URL", "http://localhost:5173")

# Base URL for our Flask app assets (must be reachable from the editor browser)
FLASK_BASE_URL = os.getenv("FLASK_BASE_URL", "http://localhost:8789")

# Static assets dir (for embedding as data URLs to avoid CORS/tainted canvas)
ASSETS_DIR = Path(__file__).parent.parent / "static" / "assets"
GENERATED_DIR = Path(__file__).parent.parent / "generated"


def _file_to_data_url(filepath: Path) -> str:
    """Read a local file and return a base64 data URL."""
    ext = filepath.suffix.lower().lstrip(".")
    mime = {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg"}.get(ext, "image/png")
    data = base64.b64encode(filepath.read_bytes()).decode("utf-8")
    return f"data:{mime};base64,{data}"


# ── Per-format layer specs ─────────────────────────────────────────────────────
# All values in pixels at the target canvas dimensions.

LAYER_SPECS = {
    "wechat_banner": {
        # 900 × 500
        "logo": {
            "left": 30, "top": 22,
            "width": 180, "height": 68,
        },
        "mountain": {
            "left": 0, "top": 330,
            "width": 900, "height": 170,
        },
        "headline": {
            "left": 30, "top": 210,
            "width": 600, "height": 120,
            "font_family": "HYQiHei-50S",
            "font_size": 56,
            "font_weight": "bold",
            "fill": "#FFFFFF",
        },
    },
    "a4_flyer": {
        # 2480 × 3508
        "logo": {
            "left": 120, "top": 120,
            "width": 600, "height": 226,
        },
        "mountain": {
            "left": 0, "top": 2900,
            "width": 2480, "height": 500,
        },
        "headline": {
            "left": 120, "top": 2680,
            "width": 2200, "height": 300,
            "font_family": "HYQiHei-50S",
            "font_size": 160,
            "font_weight": "bold",
            "fill": "#FFFFFF",
        },
    },
    "square_post": {
        # 1080 × 1080
        "logo": {
            "left": 50, "top": 50,
            "width": 220, "height": 83,
        },
        "mountain": {
            "left": 0, "top": 800,
            "width": 1080, "height": 280,
        },
        "headline": {
            "left": 50, "top": 600,
            "width": 900, "height": 180,
            "font_family": "HYQiHei-50S",
            "font_size": 72,
            "font_weight": "bold",
            "fill": "#FFFFFF",
        },
    },
}


def _nanoid() -> str:
    return uuid.uuid4().hex[:10]


def build_canvas_json(
    image_url: str,
    format_key: str,
    headline_text: str = "在此输入标题",
    mountain_variant: str = "white",  # "white" or "red"
) -> dict:
    """
    Construct the full Fabric.js canvas JSON for a given format.

    image_url: absolute URL to the resized AI background image
    format_key: one of wechat_banner, a4_flyer, square_post
    headline_text: placeholder text for the headline layer
    mountain_variant: "white" (on dark bg) or "red" (on light bg)
    """
    fmt = FORMATS[format_key]
    specs = LAYER_SPECS[format_key]
    w, h = fmt["width"], fmt["height"]

    mountain_file = "mountain_white_4.png" if mountain_variant == "white" else "mountain_red_4.png"

    # Embed static assets as data URLs — avoids CORS/tainted canvas on export
    logo_url = _file_to_data_url(ASSETS_DIR / "aia_logo_red.png")
    mountain_url = _file_to_data_url(ASSETS_DIR / mountain_file)

    # AI background: embed if file exists locally, otherwise use URL
    generated_path = GENERATED_DIR / image_url.split("/generated/")[-1] if "/generated/" in image_url else None
    if generated_path and generated_path.exists():
        image_url = _file_to_data_url(generated_path)

    logo_spec = specs["logo"]
    mtn_spec = specs["mountain"]
    txt_spec = specs["headline"]

    canvas = {
        "id": _nanoid(),
        "version": "5.3.0",
        "zoom": 1,
        "width": w,
        "height": h,
        "clip": 2,
        "workSpace": {
            "fillType": 0,
            "left": 0,
            "top": 0,
            "angle": 0,
            "scaleX": 1,
            "scaleY": 1,
        },
        "objects": [
            # 1. WorkSpaceDrawType — must be first
            {
                "type": "Rect",
                "id": "WorkSpaceDrawType",
                "name": "workspace",
                "left": 0,
                "top": 0,
                "width": w,
                "height": h,
                "fill": "#ffffff",
                "scaleX": 1,
                "scaleY": 1,
                "angle": 0,
                "opacity": 1,
                "selectable": False,
                "evented": False,
            },
            # 2. AI background image
            {
                "type": "Image",
                "id": _nanoid(),
                "name": "ai-background",
                "src": image_url,
                "crossOrigin": "anonymous",
                "left": 0,
                "top": 0,
                "width": w,
                "height": h,
                "scaleX": 1,
                "scaleY": 1,
                "angle": 0,
                "opacity": 1,
                "editable": True,
                "modified": True,
                "imageType": 0,
                "sticker": False,
                "isShow": True,
                "selectable": True,
            },
            # 3. Mountain graphic — locked brand asset
            {
                "type": "Image",
                "id": _nanoid(),
                "name": "mountain-graphic",
                "src": mountain_url,
                "crossOrigin": "anonymous",
                "left": mtn_spec["left"],
                "top": mtn_spec["top"],
                "width": mtn_spec["width"],
                "height": mtn_spec["height"],
                "scaleX": 1,
                "scaleY": 1,
                "angle": 0,
                "opacity": 1,
                "editable": False,
                "modified": True,
                "imageType": 0,
                "sticker": False,
                "isShow": True,
                "selectable": True,
            },
            # 4. AIA logo — locked brand asset
            {
                "type": "Image",
                "id": _nanoid(),
                "name": "logo",
                "src": logo_url,
                "crossOrigin": "anonymous",
                "left": logo_spec["left"],
                "top": logo_spec["top"],
                "width": logo_spec["width"],
                "height": logo_spec["height"],
                "scaleX": 1,
                "scaleY": 1,
                "angle": 0,
                "opacity": 1,
                "editable": False,
                "modified": True,
                "imageType": 0,
                "sticker": False,
                "isShow": True,
                "selectable": True,
            },
            # 5. Headline text — editable
            {
                "type": "Textbox",
                "id": _nanoid(),
                "name": "headline-text",
                "text": headline_text,
                "fontFamily": txt_spec["font_family"],
                "fontSize": txt_spec["font_size"],
                "fill": txt_spec["fill"],
                "fill_cmyk": "C0 M100 Y63 K12",
                "color_cmyk": "C0 M0 Y0 K0",
                "left": txt_spec["left"],
                "top": txt_spec["top"],
                "width": txt_spec["width"],
                "height": txt_spec["height"],
                "scaleX": 1,
                "scaleY": 1,
                "angle": 0,
                "opacity": 1,
                "editable": True,
                "isShow": True,
                "selectable": True,
                "textAlign": "left",
                "fontWeight": txt_spec.get("font_weight", "bold"),
                "lineHeight": 1.3,
            },
        ],
    }
    return canvas


def compress_canvas(canvas: dict) -> str:
    """Gzip compress canvas JSON → base64 string (pako-compatible)."""
    json_bytes = json.dumps(canvas, ensure_ascii=False).encode("utf-8")
    compressed = gzip.compress(json_bytes)
    return base64.b64encode(compressed).decode("utf-8")


def post_to_template(template_id: str, canvas: dict) -> bool:
    """POST the canvas JSON to the yft-design backend template."""
    url = f"{YFT_BACKEND_URL}/admin/template/{template_id}/pages"
    compressed = compress_canvas(canvas)

    resp = requests.put(url, json={"data": compressed}, timeout=10)
    resp.raise_for_status()
    result = resp.json()
    return result.get("code") == 200


def assemble_and_handoff(
    image_filename: str,
    format_key: str,
    headline_text: str = "在此输入标题",
    mountain_variant: str = "white",
) -> dict:
    """
    Full Step 4 pipeline:
    1. Build canvas JSON
    2. Compress and POST to template
    3. Return editor URL

    Returns: { "editor_url": str, "template_id": str }
    """
    if format_key not in TEMPLATE_IDS:
        raise ValueError(f"No template ID configured for format: {format_key}")

    template_id = TEMPLATE_IDS[format_key]
    image_url = f"{FLASK_BASE_URL}/generated/{image_filename}"

    canvas = build_canvas_json(
        image_url=image_url,
        format_key=format_key,
        headline_text=headline_text,
        mountain_variant=mountain_variant,
    )

    success = post_to_template(template_id, canvas)
    if not success:
        raise RuntimeError("Failed to update template on yft-design backend")

    editor_url = f"{YFT_FRONTEND_URL}/?template_id={template_id}"
    return {
        "editor_url": editor_url,
        "template_id": template_id,
        "canvas_id": canvas["id"],
    }
