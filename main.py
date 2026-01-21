from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import io
from PIL import Image, ImageDraw
import datetime
import os

app = FastAPI()

@app.get("/api/image")
def get_image(slide: int = None):
    now = datetime.datetime.now()
    minute = now.minute
    slide_num = slide or (minute // 10) % 3 + 1
    
    # Ищем img1.jpg, img2.jpg, img3.jpg в корне репозитория
    img_path = f"img{slide_num}.jpg"
    try:
        if os.path.exists(img_path):
            img = Image.open(img_path).convert('RGB').resize((400, 100))
        else:
            img = Image.new('RGB', (400, 100), color=(50, 100, 200))
        
        draw = ImageDraw.Draw(img)
        draw.text((20, 30), f"Slide {slide_num}", fill=(255, 255, 255))
        draw.text((20, 70), now.strftime('%H:%M'), fill=(200, 200, 200))
        
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='JPEG', quality=90)
        img_byte_arr.seek(0)
        
        return StreamingResponse(
            img_byte_arr, 
            media_type="image/jpeg",
            headers={"Cache-Control": "no-cache, no-store, must-revalidate"}
        )
    except Exception as e:
        # Показываем ошибку на картинке
        img = Image.new('RGB', (400, 100), color=(255, 0, 0))
        draw = ImageDraw.Draw(img)
        draw.text((10, 10), "Error: " + str(e)[:50], fill=(255, 255, 255))
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='JPEG')
        return StreamingResponse(img_byte_arr, media_type="image/jpeg")

@app.get("/")
def root():
    return {"status": "OK", "endpoint": "/api/image"}
