from celery import shared_task
from PIL import Image, ImageDraw, ImageFont
from django.conf import settings
from .models import Mockup
import os
import uuid

@shared_task(bind=True)
def generate_mockup_task(self, mockup_id):
    mockup = Mockup.objects.get(id=mockup_id)

    base_image_path = os.path.join(settings.BASE_DIR, 'static', 'images', f'{mockup.shirt_color}.png')
    if not os.path.exists(base_image_path):
        base_image_path = os.path.join(settings.BASE_DIR, 'static', 'images', 'white.png')

    img = Image.open(base_image_path).convert("RGBA")
    draw = ImageDraw.Draw(img)

    fonts_dir = os.path.join(settings.BASE_DIR, 'static', 'fonts')
    os.makedirs(fonts_dir, exist_ok=True)

    font_name = mockup.font or 'arial'
    if not font_name.lower().endswith('.ttf'):
        font_name += '.ttf'

    custom_font_path = os.path.join(fonts_dir, font_name)
    default_font_path = os.path.join(settings.BASE_DIR, 'arial.ttf')

    if os.path.exists(custom_font_path):
        font_path = custom_font_path
    elif os.path.exists(default_font_path):
        font_path = default_font_path
    else:
        font_path = None

    if font_path:
        try:
            font = ImageFont.truetype(font_path, 40)
        except Exception:
            font = ImageFont.load_default()
    else:
        font = ImageFont.load_default()

    text_color = mockup.text_color or "#000000"
    text = mockup.text

    try:
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
    except AttributeError:
        try:
            text_width, text_height = draw.textsize(text, font=font)
        except AttributeError:
            text_width = draw.textlength(text, font=font)
            text_height = font.size if hasattr(font, 'size') else 40

    image_width, image_height = img.size
    x = (image_width - text_width) / 2
    y = (image_height - text_height) / 2

    draw.text((x, y), text, font=font, fill=text_color)

    filename = f"{uuid.uuid4()}.png"
    output_dir = os.path.join(settings.MEDIA_ROOT, 'mockups')
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, filename)
    img.convert("RGB").save(output_path, "PNG")

    mockup.image.name = f"mockups/{filename}"
    mockup.save()

    return {
        "mockup_id": mockup.id,
        "image_url": mockup.image.url,
        "shirt_color": mockup.shirt_color,
        "font_used": font_name,
    }
