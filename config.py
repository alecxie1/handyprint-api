import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

FORMATS = {
    "wechat_banner": {
        "label": "WeChat Banner",
        "width": 900,
        "height": 500,
        "gen_size": "1536x1024",
        "logo_zone": {"x": 30, "y": 20, "max_width": 180},
        "text_zone": {"x": 0, "y": 340, "width": 900, "height": 160},
        "mountain_zone": {"x": 0, "y": 350, "width": 900, "height": 150},
    },
    "a4_flyer": {
        "label": "A4 Flyer (300 DPI)",
        "width": 2480,
        "height": 3508,
        "gen_size": "1024x1536",
        "logo_zone": {"x": 80, "y": 80, "max_width": 400},
        "text_zone": {"x": 0, "y": 2600, "width": 2480, "height": 800},
        "mountain_zone": {"x": 0, "y": 2700, "width": 2480, "height": 808},
    },
    "square_post": {
        "label": "Square Social Post",
        "width": 1080,
        "height": 1080,
        "gen_size": "1024x1024",
        "logo_zone": {"x": 40, "y": 40, "max_width": 220},
        "text_zone": {"x": 0, "y": 750, "width": 1080, "height": 330},
        "mountain_zone": {"x": 0, "y": 780, "width": 1080, "height": 300},
    },
}

BRANDS_DIR = os.path.join(os.path.dirname(__file__), "brands")
UPLOADS_DIR = os.path.join(os.path.dirname(__file__), "uploads")
GENERATED_DIR = os.path.join(os.path.dirname(__file__), "generated")

# yft-design backend URL (our mini backend or Kevin's)
YFT_BACKEND_URL = os.getenv("YFT_BACKEND_URL", "http://localhost:8789")

# Template IDs — created via handy-backend, one per format
TEMPLATE_IDS = {
    "wechat_banner": os.getenv("TEMPLATE_ID_WECHAT_BANNER", "v3euYUaMDX"),
    "a4_flyer": os.getenv("TEMPLATE_ID_A4_FLYER", "07qvMFBqhN"),
    "square_post": os.getenv("TEMPLATE_ID_SQUARE_POST", "v1JvLFg3IC"),
}

BRAND_PROFILE_SCHEMA = {
    "type": "object",
    "properties": {
        "colors": {
            "type": "object",
            "properties": {
                "dominant": {"type": "string"},
                "supporting": {"type": "array", "items": {"type": "string"}},
                "accent": {"type": "array", "items": {"type": "string"}},
                "typical_background": {"type": "string"},
                "color_mood": {"type": "string"},
                "forbidden": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["dominant", "supporting", "accent", "typical_background", "color_mood", "forbidden"],
            "additionalProperties": False,
        },
        "typography": {
            "type": "object",
            "properties": {
                "style": {"type": "string"},
                "weight": {"type": "string"},
                "headline_treatment": {"type": "string"},
                "chinese_text_style": {"type": "string"},
                "size_hierarchy": {"type": "string"},
                "text_density": {"type": "string"},
            },
            "required": ["style", "weight", "headline_treatment", "chinese_text_style", "size_hierarchy", "text_density"],
            "additionalProperties": False,
        },
        "lighting": {
            "type": "object",
            "properties": {
                "style": {"type": "string"},
                "direction": {"type": "string"},
                "temperature": {"type": "string"},
                "shadow_quality": {"type": "string"},
            },
            "required": ["style", "direction", "temperature", "shadow_quality"],
            "additionalProperties": False,
        },
        "camera_perspective": {
            "type": "object",
            "properties": {
                "angle": {"type": "string"},
                "composition_rule": {"type": "string"},
                "depth_of_field": {"type": "string"},
                "negative_space": {"type": "string"},
            },
            "required": ["angle", "composition_rule", "depth_of_field", "negative_space"],
            "additionalProperties": False,
        },
        "rendering_style": {"type": "string"},
        "texture": {
            "type": "object",
            "properties": {
                "dominant_surface": {"type": "string"},
                "feel": {"type": "string"},
            },
            "required": ["dominant_surface", "feel"],
            "additionalProperties": False,
        },
        "composition": {
            "type": "object",
            "properties": {
                "layout_type": {"type": "string"},
                "focal_point": {"type": "string"},
                "text_zone": {"type": "string"},
                "element_density": {"type": "string"},
            },
            "required": ["layout_type", "focal_point", "text_zone", "element_density"],
            "additionalProperties": False,
        },
        "signature_elements": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "role": {"type": "string"},
                    "typical_placement": {"type": "string"},
                    "color_treatment": {"type": "string"},
                    "prominence": {"type": "string"},
                    "rules": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["name", "role", "typical_placement", "color_treatment", "prominence", "rules"],
                "additionalProperties": False,
            },
        },
        "photography": {
            "type": "object",
            "properties": {
                "present": {"type": "boolean"},
                "subject": {"type": "string"},
                "style": {"type": "string"},
                "mood": {"type": "string"},
            },
            "required": ["present", "subject", "style", "mood"],
            "additionalProperties": False,
        },
        "background_treatment": {"type": "string"},
        "brand_mood": {"type": "array", "items": {"type": "string"}},
        "visual_tone": {"type": "string"},
        "logo_placement": {"type": "string"},
        "what_to_avoid": {"type": "array", "items": {"type": "string"}},
    },
    "required": [
        "colors", "typography", "lighting", "camera_perspective", "rendering_style",
        "texture", "composition", "signature_elements", "photography",
        "background_treatment", "brand_mood", "visual_tone", "logo_placement", "what_to_avoid"
    ],
    "additionalProperties": False,
}
