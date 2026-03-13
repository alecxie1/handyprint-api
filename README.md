# handyprint-api — 延展设计 Flask Backend

Steps 1–3 of the AI brand extension pipeline.

## Setup

```bash
cd ~/projects/handyprint-api

# Install deps
pip3 install --break-system-packages -r requirements.txt

# Copy env
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY

# Run
python3 app.py
# → http://localhost:5000
```

## Also Start the Editor Backend

```bash
cd ~/projects/handy-backend
npm install && node server.js
# → http://localhost:8789
```

## What's Built

| Step | File | Status |
|---|---|---|
| Step 1: Brand analysis (GPT-4o Vision) | `services/vision.py` | ✅ |
| Step 2: Prompt assembly (GPT-4o) | `services/prompt.py` | ✅ |
| Step 3: Image generation (GPT Image 1.5) | `services/image_gen.py` | ✅ |
| Step 3.5: Pillow resize to canvas | `services/resize.py` | ✅ |
| Screen 1–5 UI | `templates/` | ✅ |
| Step 4: Canvas assembly → yft-design | Pending template IDs | ⏳ |

## What's Needed for Step 4

1. Run handy-backend: `cd ~/projects/handy-backend && node server.js`
2. Create 3 templates (see handy-backend/README.md)
3. Copy font files into `~/projects/handy-backend/fonts/`
4. Add template IDs to this app's `.env`

## Directory Structure

```
handyprint-api/
  app.py            # Flask entry point (port 5000)
  config.py         # Format specs, API keys, JSON schema
  routes/
    brand.py        # POST /api/brands/analyze, GET /api/brands
    generate.py     # POST /api/prompt/assemble, POST /api/generate
  services/
    vision.py       # GPT-4o Vision → brand profile JSON
    prompt.py       # GPT-4o → assembled generation prompt
    image_gen.py    # GPT Image 1.5 → 4 background variations
    resize.py       # Pillow resize to canvas dimensions
  templates/        # Jinja2 HTML (5 screens)
  brands/           # Saved brand profiles (JSON)
  uploads/          # Temp upload storage
  generated/        # Output images
```
