from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
import io
from PIL import Image, ImageDraw
import datetime
import os
import random

app = FastAPI()

# Монтируем папку public для статических файлов
app.mount("/public", StaticFiles(directory="public"), name="public")

@app.get("/api/image")
def get_image(slide: int = None):
    # Меняем по времени/параметру (3 изображения)
    now = datetime.datetime.now()
    minute = now.minute
    slide_num = slide or (minute // 10) % 3 + 1
    
    # Читаем изображение из репозитория
    img_path = f"public/img{slide_num}.jpg"  # JPG файлы
    if os.path.exists(img_path):
        img = Image.open(img_path).convert('RGB').resize((400, 100))
    else:
        # Fallback: генерируем
        img = Image.new('RGB', (400, 100), color=(50, 100, 200))
    
    draw = ImageDraw.Draw(img)
    draw.text((20, 30), f"Слайд {slide_num}", fill=(255, 255, 255))
    draw.text((20, 70), now.strftime('%H:%M'), fill=(200, 200, 200))
    
    # JPG формат!
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='JPEG', quality=90)  # quality 0-95
    img_byte_arr.seek(0)
    
    return StreamingResponse(
        img_byte_arr, 
        media_type="image/jpeg",  # Важно для браузера/GitHub!
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache"
        }
    )

@app.get("/")
def root():
    return {"message": "Готово! /api/image (JPG) или /public/img1.jpg"}
