import requests
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
from io import BytesIO
import random
from dotenv import load_dotenv
from os import getenv

load_dotenv()

def fetch_and_resize_image_from_unsplash(query, target_size=(1024, 1024)):
    access_key = getenv("UNSPLASH_ACCESS_KEY")
    url = f"https://api.unsplash.com/photos/random?query={query}&client_id={access_key}"
    
    response = requests.get(url)
    if response.status_code == 200:
        json_response = response.json()
        image_url = json_response['urls']['full']
        image_response = requests.get(image_url)
        img = Image.open(BytesIO(image_response.content))
        img.thumbnail(target_size, Image.Resampling.LANCZOS)
        return img
    else:
        raise Exception("Error fetching image:", response.status_code, response.text)

categoryes = ["age", "alone", "amazing", "anger", "architecture", "art", "attitude", "beauty", "best", "birthday", "business", "car", "change", "communication", "computers", "cool", "courage", "dad", "dating", "death", "design", "dreams", "education", "environmental", "equality", "experience", "failure", "faith", "family", "famous", "fear", "fitness", "food", "forgiveness", "freedom", "friendship", "funny", "future", "god", "good", "government", "graduation", "great", "happiness", "health", "history", "home", "hope", "humor", "imagination", "inspirational", "intelligence", "jealousy", "knowledge", "leadership", "learning", "legal", "life", "love", "marriage", "medical", "men", "mom", "money", "morning", "movies", "success"]
category = random.choice(categoryes)
def fetch_quote(category):
    api_url = f'https://api.api-ninjas.com/v1/quotes?category={category}'
    response = requests.get(api_url, headers={'X-Api-Key': getenv("API_NINJAS_API_KEY")})
    if response.status_code == requests.codes.ok:
        quote_data = response.json()[0]  # Get the first quote from the list
        return quote_data['quote'], quote_data['author']
    else:
        raise Exception("Error fetching quote:", response.status_code, response.text)

def wrap_text(text, font, max_width):
    lines = []
    words = text.split()
    while words:
        line = ''
        while words and font.getlength(line + words[0]) <= max_width:
            line = line + (words.pop(0) + ' ')
        lines.append(line.strip())
    return lines

quote_text, author = fetch_quote(category)
background_image = fetch_and_resize_image_from_unsplash(category, target_size=(1024, 1024))
enhancer = ImageEnhance.Contrast(background_image)
background_image = enhancer.enhance(1.5)
overlay = Image.new('RGBA', background_image.size, (0, 0, 0, 100))
background_image = Image.alpha_composite(background_image.convert('RGBA'), overlay)
quote_font = ImageFont.truetype("arial.ttf", 36)
author_font = ImageFont.truetype("arial.ttf", 28)
wrapped_text = wrap_text(f"\"{quote_text}\"", quote_font, background_image.width - 100)
author_text = f"- {author}"
draw = ImageDraw.Draw(background_image)
total_text_height = sum([draw.textbbox((0, 0), line, font=quote_font)[3] - draw.textbbox((0, 0), line, font=quote_font)[1] for line in wrapped_text])
total_text_height += draw.textbbox((0, 0), author_text, font=author_font)[3] - draw.textbbox((0, 0), author_text, font=author_font)[1]
total_text_height += (len(wrapped_text) - 1) * 10
current_y = (background_image.height - total_text_height) / 2
shadow_offset = (2, 2)
for line in wrapped_text:
    text_width, text_height = draw.textbbox((0, 0), line, font=quote_font)[2:]
    text_x = (background_image.width - text_width) / 2
    draw.text((text_x + shadow_offset[0], current_y + shadow_offset[1]), line, font=quote_font, fill="black")
    draw.text((text_x, current_y), line, font=quote_font, fill="white")
    current_y += text_height + 10

author_width, author_height = draw.textbbox((0, 0), author_text, font=author_font)[2:]
author_x = (background_image.width - author_width) / 2
draw.text((author_x + shadow_offset[0], current_y + shadow_offset[1]), author_text, font=author_font, fill="black")
draw.text((author_x, current_y), author_text, font=author_font, fill="white")
background_image.show()
background_image.convert('RGB').save("quote_image.png")