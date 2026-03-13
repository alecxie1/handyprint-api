import base64
import os
import uuid
from openai import OpenAI
from config import OPENAI_API_KEY, FORMATS, GENERATED_DIR

client = OpenAI(api_key=OPENAI_API_KEY)

# Map format key → nearest supported GPT Image 1.5 size
FORMAT_TO_GEN_SIZE = {
    "wechat_banner": "1536x1024",   # landscape
    "a4_flyer": "1024x1536",        # portrait
    "square_post": "1024x1024",     # square
}


def generate_images(prompt: str, format_key: str, n: int = 4) -> list[str]:
    """
    Generate n background images using GPT Image 1.5.
    Returns list of local file paths to the raw generated images (before resize).
    """
    size = FORMAT_TO_GEN_SIZE.get(format_key, "1024x1024")

    response = client.images.generate(
        model="gpt-image-1",
        prompt=prompt,
        n=n,
        size=size,
        quality="high",
    )

    saved_paths = []
    run_id = uuid.uuid4().hex[:8]

    for i, img_data in enumerate(response.data):
        filename = f"{run_id}_v{i+1}_raw.png"
        filepath = os.path.join(GENERATED_DIR, filename)

        if img_data.b64_json:
            img_bytes = base64.b64decode(img_data.b64_json)
            with open(filepath, "wb") as f:
                f.write(img_bytes)
        elif img_data.url:
            import urllib.request
            urllib.request.urlretrieve(img_data.url, filepath)
        else:
            continue

        saved_paths.append(filepath)

    return saved_paths
