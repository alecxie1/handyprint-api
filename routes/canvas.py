from flask import Blueprint, request, jsonify
from services.canvas import assemble_and_handoff

canvas_bp = Blueprint("canvas", __name__)


@canvas_bp.route("/api/canvas/assemble", methods=["POST"])
def assemble():
    """
    Step 4: Build Fabric.js canvas and hand off to yft-design editor.
    Body: { image_filename, format_key, headline_text?, mountain_variant? }
    Returns: { editor_url, template_id }
    """
    data = request.get_json()
    image_filename = data.get("image_filename", "").strip()
    format_key = data.get("format_key", "").strip()
    headline_text = data.get("headline_text", "在此输入标题").strip()
    mountain_variant = data.get("mountain_variant", "white")

    if not image_filename or not format_key:
        return jsonify({"error": "image_filename and format_key are required"}), 400

    try:
        result = assemble_and_handoff(
            image_filename=image_filename,
            format_key=format_key,
            headline_text=headline_text,
            mountain_variant=mountain_variant,
        )
        return jsonify({"success": True, **result})
    except Exception as e:
        return jsonify({"error": f"Canvas assembly failed: {str(e)}"}), 500
