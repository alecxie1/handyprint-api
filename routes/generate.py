import json
import os
from flask import Blueprint, request, jsonify, send_from_directory
from config import FORMATS, BRANDS_DIR, GENERATED_DIR
from services.prompt import assemble_prompt
from services.image_gen import generate_images
from services.resize import resize_all

generate_bp = Blueprint("generate", __name__)


@generate_bp.route("/api/prompt/assemble", methods=["POST"])
def assemble():
    """
    Step 2: Assemble generation prompt from brand profile + format + campaign description.
    Body: { client_name, format_key, campaign_description }
    """
    data = request.get_json()
    client_name = data.get("client_name", "").strip()
    format_key = data.get("format_key", "").strip()
    campaign_description = data.get("campaign_description", "").strip()

    if not all([client_name, format_key, campaign_description]):
        return jsonify({"error": "client_name, format_key, and campaign_description are required"}), 400

    if format_key not in FORMATS:
        return jsonify({"error": f"Unknown format. Choose from: {list(FORMATS.keys())}"}), 400

    profile_path = os.path.join(BRANDS_DIR, f"{client_name}.json")
    if not os.path.exists(profile_path):
        return jsonify({"error": f"Brand profile '{client_name}' not found"}), 404

    with open(profile_path, "r", encoding="utf-8") as f:
        brand_profile = json.load(f)

    try:
        prompt = assemble_prompt(brand_profile, format_key, campaign_description)
    except Exception as e:
        return jsonify({"error": f"Prompt assembly failed: {str(e)}"}), 500

    return jsonify({
        "prompt": prompt,
        "client_name": client_name,
        "format_key": format_key,
        "format_label": FORMATS[format_key]["label"],
    })


@generate_bp.route("/api/generate", methods=["POST"])
def generate():
    """
    Steps 3 + 3.5: Generate images from approved prompt, then resize to canvas dimensions.
    Body: { prompt, format_key, client_name }
    Returns: list of { path, url, width, height }
    """
    data = request.get_json()
    prompt = data.get("prompt", "").strip()
    format_key = data.get("format_key", "").strip()
    client_name = data.get("client_name", "unknown")

    if not prompt or not format_key:
        return jsonify({"error": "prompt and format_key are required"}), 400

    if format_key not in FORMATS:
        return jsonify({"error": f"Unknown format"}), 400

    fmt = FORMATS[format_key]

    # Step 3: Generate raw images
    try:
        raw_paths = generate_images(prompt, format_key, n=4)
    except Exception as e:
        return jsonify({"error": f"Image generation failed: {str(e)}"}), 500

    if not raw_paths:
        return jsonify({"error": "No images were generated"}), 500

    # Step 3.5: Resize to target canvas dimensions
    try:
        final_paths = resize_all(raw_paths, format_key)
    except Exception as e:
        return jsonify({"error": f"Image resize failed: {str(e)}"}), 500

    results = []
    for path in final_paths:
        filename = os.path.basename(path)
        results.append({
            "filename": filename,
            "url": f"/generated/{filename}",
            "width": fmt["width"],
            "height": fmt["height"],
        })

    return jsonify({
        "success": True,
        "format_key": format_key,
        "format": fmt,
        "images": results,
        "client_name": client_name,
    })


@generate_bp.route("/generated/<filename>")
def serve_generated(filename):
    """Serve generated image files."""
    return send_from_directory(GENERATED_DIR, filename)
