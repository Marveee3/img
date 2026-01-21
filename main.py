from fastapi import FastAPI, Response
from fastapi.responses import StreamingResponse
import io
from PIL import Image, ImageDraw, ImageFont
import datetime
import os
import random

app = FastAPI()

# Кэш для хранения времени последнего обновления
image_cache = {}

def generate_image(slide_num: int, use_time_based: bool = True):
    """Генерация или загрузка изображения"""
    now = datetime.datetime.now()
    
    # Генерируем уникальный ключ для 30-секундного интервала
    if use_time_based:
        # Меняем каждые 30 секунд
        time_key = int(now.timestamp()) // 30
        cache_key = f"slide_{slide_num}_time_{time_key}"
    else:
        cache_key = f"slide_{slide_num}"
    
    # Проверяем кэш
    if cache_key in image_cache:
        return image_cache[cache_key]
    
    try:
        # Пробуем загрузить изображение из файла
        img_path = f"img{slide_num}.jpg"
        if os.path.exists(img_path):
            img = Image.open(img_path).convert('RGB').resize((400, 200))
        else:
            # Генерируем случайный цвет для фона
            r = random.randint(0, 255)
            g = random.randint(0, 255)
            b = random.randint(0, 255)
            img = Image.new('RGB', (400, 200), color=(r, g, b))
        
        draw = ImageDraw.Draw(img)
        
        # Пробуем использовать системный шрифт, иначе используем стандартный
        try:
            font = ImageFont.truetype("arial.ttf", 24)
            font_small = ImageFont.truetype("arial.ttf", 18)
        except:
            font = ImageFont.load_default()
            font_small = ImageFont.load_default()
        
        # Добавляем текст
        draw.text((20, 30), f"Slide {slide_num}", fill=(255, 255, 255), font=font)
        draw.text((20, 70), now.strftime('%H:%M:%S'), fill=(200, 200, 200), font=font)
        draw.text((20, 100), f"Interval: {(int(now.timestamp()) // 30)}", 
                 fill=(220, 220, 220), font=font_small)
        draw.text((20, 130), "Updates every 30 seconds", 
                 fill=(180, 180, 255), font=font_small)
        
        # Сохраняем в буфер
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='JPEG', quality=95)
        img_data = img_byte_arr.getvalue()
        
        # Кэшируем
        image_cache[cache_key] = img_data
        return img_data
        
    except Exception as e:
        # Создаем изображение с ошибкой
        img = Image.new('RGB', (400, 200), color=(255, 50, 50))
        draw = ImageDraw.Draw(img)
        draw.text((10, 10), f"Error: {str(e)[:40]}", fill=(255, 255, 255))
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='JPEG')
        return img_byte_arr.getvalue()

@app.get("/api/image")
def get_image(slide: int = None):
    """Основной endpoint для получения изображения"""
    now = datetime.datetime.now()
    
    # Автоматически определяем слайд если не указан
    if slide is None:
        # Меняем слайд каждые 30 секунд
        time_interval = int(now.timestamp()) // 30
        slide_num = (time_interval % 3) + 1  # Цикл по 3 слайда
    else:
        slide_num = slide
    
    # Генерируем изображение
    img_data = generate_image(slide_num, use_time_based=True)
    
    # Возвращаем изображение с заголовками для предотвращения кэширования
    return Response(
        content=img_data,
        media_type="image/jpeg",
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate, max-age=0",
            "Pragma": "no-cache",
            "Expires": "0",
            "Last-Modified": now.strftime('%a, %d %b %Y %H:%M:%S GMT'),
            "ETag": f'"{int(now.timestamp())}"'
        }
    )

@app.get("/api/image/{slide_num}")
def get_specific_image(slide_num: int):
    """Endpoint для получения конкретного слайда"""
    img_data = generate_image(slide_num, use_time_based=False)
    return Response(
        content=img_data,
        media_type="image/jpeg",
        headers={"Cache-Control": "no-cache, no-store, must-revalidate"}
    )

@app.get("/api/status")
def get_status():
    """Endpoint для проверки статуса и получения информации"""
    now = datetime.datetime.now()
    time_interval = int(now.timestamp()) // 30
    current_slide = (time_interval % 3) + 1
    
    return {
        "status": "OK",
        "current_time": now.isoformat(),
        "current_slide": current_slide,
        "time_interval": time_interval,
        "endpoints": {
            "auto_image": "/api/image",
            "specific_image": "/api/image/{slide_num}",
            "status": "/api/status"
        }
    }

@app.get("/")
def root():
    return {"status": "OK", "message": "Image API is running"}
