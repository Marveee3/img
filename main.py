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
    
    # Читаем JPG напрямую из репозитория (даже без public/)
    img_path = f"img{slide_num}.jpg"  # Положи img1.jpg, img2.jpg в корень repo
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
        img = Image.new('RGB', (400, 100), color=(255, 0, 0))
        d = ImageDraw.Draw(img)
        d.text((10, 50), str(e), fill=(255, 255, 255))
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='JPEG')
        img_byte_arr.seek(0)
        return StreamingResponse(img_byte_arr, media_type="image/jpeg")

@app.get("/")
def root():
    return {"message": "API работает! /api/image"}
