import json
import os
import uuid
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from config import BRANDS_DIR, UPLOADS_DIR
from services.vision import extract_brand_profile, pdf_to_images

brand_bp = Blueprint("brand", __name__)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "pdf"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@brand_bp.route("/api/brands", methods=["GET"])
def list_brands():
    """List all saved brand profiles."""
    brands = []
    for f in os.listdir(BRANDS_DIR):
        if f.endswith(".json"):
            brands.append(f.replace(".json", ""))
    return jsonify({"brands": sorted(brands)})


@brand_bp.route("/api/brands/<client_name>", methods=["GET"])
def get_brand(client_name):
    """Load a saved brand profile."""
    path = os.path.join(BRANDS_DIR, f"{client_name}.json")
    if not os.path.exists(path):
        return jsonify({"error": "Brand profile not found"}), 404
    with open(path, "r", encoding="utf-8") as f:
        profile = json.load(f)
    return jsonify({"profile": profile, "client_name": client_name})


@brand_bp.route("/api/brands/analyze", methods=["POST"])
def analyze_brand():
    """
    Accept uploaded brand assets, run GPT-4o Vision extraction,
    save the profile, and return it.
    """
    client_name = request.form.get("client_name", "").strip()
    if not client_name:
        return jsonify({"error": "client_name is required"}), 400

    if "files" not in request.files:
        return jsonify({"error": "No files uploaded"}), 400

    files = request.files.getlist("files")
    if not files:
        return jsonify({"error": "No files selected"}), 400

    # Save uploaded files
    session_id = uuid.uuid4().hex[:8]
    session_dir = os.path.join(UPLOADS_DIR, session_id)
    os.makedirs(session_dir, exist_ok=True)

    image_paths = []

    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            save_path = os.path.join(session_dir, filename)
            file.save(save_path)

            ext = filename.rsplit(".", 1)[1].lower()
            if ext == "pdf":
                # Convert PDF pages to images
                pdf_images = pdf_to_images(save_path, session_dir)
                image_paths.extend(pdf_images)
            else:
                image_paths.append(save_path)
        else:
            return jsonify({"error": f"Unsupported file type: {file.filename}. Use PNG, JPG, or PDF."}), 400

    if not image_paths:
        return jsonify({"error": "No valid images found after processing uploads"}), 400

    # Cap at 10 images for API efficiency
    image_paths = image_paths[:10]

    try:
        profile = extract_brand_profile(image_paths)
    except Exception as e:
        return jsonify({"error": f"Brand extraction failed: {str(e)}"}), 500

    # Save profile to disk
    safe_name = secure_filename(client_name)
    profile_path = os.path.join(BRANDS_DIR, f"{safe_name}.json")
    with open(profile_path, "w", encoding="utf-8") as f:
        json.dump(profile, f, ensure_ascii=False, indent=2)

    return jsonify({
        "success": True,
        "client_name": safe_name,
        "profile": profile,
    })


@brand_bp.route("/api/brands/<client_name>", methods=["PUT"])
def update_brand(client_name):
    """Save a manually edited brand profile."""
    profile = request.get_json()
    if not profile:
        return jsonify({"error": "No profile data provided"}), 400

    safe_name = secure_filename(client_name)
    profile_path = os.path.join(BRANDS_DIR, f"{safe_name}.json")
    with open(profile_path, "w", encoding="utf-8") as f:
        json.dump(profile, f, ensure_ascii=False, indent=2)

    return jsonify({"success": True, "client_name": safe_name})
