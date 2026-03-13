import json
from openai import OpenAI
from config import OPENAI_API_KEY, FORMATS

client = OpenAI(api_key=OPENAI_API_KEY)

SYSTEM_PROMPT = """You are an expert AI image generation prompt engineer specializing in brand-consistent marketing visuals.

You will receive:
1. A brand style profile (JSON) describing a client's visual identity
2. A target output format and dimensions
3. A campaign description in natural language (may be in Chinese or English)

Your task: Write a single, detailed, fluent image generation prompt that:
- Accurately represents the brand's visual identity from the style profile
- Incorporates the campaign intent from the description
- Specifies the correct format, dimensions, and composition
- Explicitly instructs the model NOT to place any logo or wordmark (logo is added as a separate layer in canvas assembly)
- Reserves the appropriate canvas zone for text overlay (text is added as a separate layer)
- Is specific enough that an image generation model can execute it precisely

Output only the generation prompt. No explanation, no preamble."""

SAFETY_SUFFIX = (
    "\n\nCRITICAL: Do not place a logo, wordmark, brand name, or brand identifier anywhere in the image. "
    "Leave the lower third of the composition completely clear of graphic elements — "
    "this area is reserved for text overlay that will be added programmatically."
)


def assemble_prompt(brand_profile: dict, format_key: str, campaign_description: str) -> str:
    """
    Use GPT-4o to assemble a generation prompt from brand profile + format + campaign description.
    Returns the assembled prompt string.
    """
    fmt = FORMATS[format_key]
    format_info = (
        f"Format: {fmt['label']}\n"
        f"Dimensions: {fmt['width']}×{fmt['height']}px\n"
        f"Text safe zone: lower {fmt['text_zone']['height']}px reserved for text overlay"
    )

    user_message = (
        f"Brand Style Profile:\n{json.dumps(brand_profile, ensure_ascii=False, indent=2)}\n\n"
        f"Target Format:\n{format_info}\n\n"
        f"Campaign Description:\n{campaign_description}"
    )

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        max_tokens=1024,
    )

    assembled = response.choices[0].message.content.strip()
    return assembled + SAFETY_SUFFIX
