import asyncio
import base64
import os
import uuid
from io import BytesIO

from PIL import Image
from fastapi import FastAPI, UploadFile, File, Form
from starlette.responses import HTMLResponse, FileResponse
from starlette.staticfiles import StaticFiles

from app.websocket import pubsub

from app.celery import celery_app

from app.db.init_db import init_db
from app.api import auth, image, ws

import uvicorn

app = FastAPI()
app.include_router(auth.router)
app.include_router(image.router)
app.include_router(ws.router)
init_db()

app.mount("/static", StaticFiles(directory="static"), name="static")

# Убедись, что папка 'static' существует
os.makedirs("static", exist_ok=True)


@app.on_event("startup")
async def startup_event():
    pubsub.EVENT_LOOP = asyncio.get_event_loop()

@app.get("/", response_class=HTMLResponse, tags=["HTML-форма"])
async def main():
    return """
    <html>
        <body>
            <h2>Вставь base64-текст → получи картинку:</h2>
            <form action="/show-image" method="post">
                <textarea name="base64_text" rows="15" cols="80" placeholder="Вставь сюда base64 изображение"></textarea><br>
                <input type="submit" value="Показать изображение">
            </form>
        </body>
    </html>
    """

@app.post("/show-image", response_class=HTMLResponse, tags=["HTML-форма"], description="Показывает изображение, декодированное из base64")
async def show_image(base64_text: str = Form(...)):
    try:
        image_data = base64.b64decode(base64_text)
        image = Image.open(BytesIO(image_data))

        filename = f"{uuid.uuid4()}.png"
        filepath = os.path.join("static", filename)
        image.save(filepath)

        return f"""
        <html>
            <body>
                <h2>Вот изображение:</h2>
                <img src="/static/{filename}" alt="Decoded Image"/><br><br>
                <a href="/">← Назад</a>
            </body>
        </html>
        """
    except Exception as e:
        return f"""
        <html>
            <body>
                <h2 style="color:red;">Ошибка:</h2>
                <p>{str(e)}</p>
                <a href="/">← Назад</a>
            </body>
        </html>
        """

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)