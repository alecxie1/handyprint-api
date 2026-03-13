import os
from flask import Flask, render_template, send_from_directory
from config import BRANDS_DIR, UPLOADS_DIR, GENERATED_DIR
from routes.brand import brand_bp
from routes.generate import generate_bp
from routes.canvas import canvas_bp

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024  # 50MB upload limit

# Ensure directories exist
for d in [BRANDS_DIR, UPLOADS_DIR, GENERATED_DIR]:
    os.makedirs(d, exist_ok=True)

# Register blueprints
app.register_blueprint(brand_bp)
app.register_blueprint(generate_bp)
app.register_blueprint(canvas_bp)


# ── UI Routes ──────────────────────────────────────────────────────────────────

@app.route("/")
def screen1():
    """Screen 1 — Brand Setup"""
    return render_template("index.html")


@app.route("/profile")
def screen2():
    """Screen 2 — Brand Profile Preview"""
    return render_template("profile.html")


@app.route("/generate")
def screen3():
    """Screen 3 — Generation Setup"""
    return render_template("generate.html")


@app.route("/review")
def screen4():
    """Screen 4 — Prompt Review"""
    return render_template("review.html")


@app.route("/results")
def screen5():
    """Screen 5 — Results"""
    return render_template("results.html")


@app.route("/static/<path:filename>")
def static_files(filename):
    return send_from_directory("static", filename)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
