import base64
import json
import os
from openai import OpenAI
from config import OPENAI_API_KEY, BRAND_PROFILE_SCHEMA

client = OpenAI(api_key=OPENAI_API_KEY)

SYSTEM_PROMPT = """You are a professional brand identity analyst. Analyze the provided brand reference images and extract a structured brand style profile.

Be specific and precise. Use exact hex color codes where visible. Identify signature graphic elements, photography style, composition patterns, and visual rules that define this brand's identity.

For Chinese brands, pay special attention to Chinese typography treatment and any brand-specific graphic motifs."""


def images_to_base64(file_paths: list[str]) -> list[dict]:
    """Convert image file paths to base64 content blocks for the API."""
    content = []
    for path in file_paths:
        ext = os.path.splitext(path)[1].lower()
        mime = {
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".gif": "image/gif",
            ".webp": "image/webp",
        }.get(ext, "image/jpeg")

        with open(path, "rb") as f:
            data = base64.standard_b64encode(f.read()).decode("utf-8")

        content.append({
            "type": "image_url",
            "image_url": {"url": f"data:{mime};base64,{data}", "detail": "high"},
        })
    return content


def pdf_to_images(pdf_path: str, output_dir: str, max_pages: int = 5) -> list[str]:
    """Convert PDF pages to images using PyMuPDF. Returns list of image paths."""
    import fitz  # PyMuPDF

    doc = fitz.open(pdf_path)
    image_paths = []
    pages_to_process = min(len(doc), max_pages)

    for i in range(pages_to_process):
        page = doc[i]
        mat = fitz.Matrix(2.0, 2.0)  # 2x zoom for better resolution
        pix = page.get_pixmap(matrix=mat)
        img_path = os.path.join(output_dir, f"pdf_page_{i+1}.png")
        pix.save(img_path)
        image_paths.append(img_path)

    doc.close()
    return image_paths


def extract_brand_profile(image_paths: list[str]) -> dict:
    """
    Run GPT-4o Vision with Structured Outputs to extract a brand profile.
    Returns the profile dict.
    """
    image_content = images_to_base64(image_paths)

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": [
                *image_content,
                {
                    "type": "text",
                    "text": (
                        "Analyze these brand reference images and extract a complete brand style profile. "
                        "Be specific about colors (use hex codes), typography, composition patterns, "
                        "signature graphic elements, photography style, and visual rules. "
                        "Return the structured profile matching the required schema exactly."
                    ),
                },
            ],
        },
    ]

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "brand_profile",
                "strict": True,
                "schema": BRAND_PROFILE_SCHEMA,
            },
        },
        max_tokens=4096,
    )

    return json.loads(response.choices[0].message.content)
