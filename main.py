from fastapi import FastAPI, HTTPException, Request, Query
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List
from bs4 import BeautifulSoup
from docx import Document
import os
import hashlib
import requests
import aiohttp
import jwt
import time
from pathlib import Path
import docx2pdf
from parser import main

app = FastAPI()

JWT_SECRET = "lD7DsO0mFVWgt4isJNuY7IcM8fUWwrAh"
JWT_ALGORITHM = "HS256"

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/preview", StaticFiles(directory="preview"), name="preview")
app.mount("/converted_files", StaticFiles(directory="converted_files"), name="converted_files")

class Template(BaseModel):
    id: int
    title: str
    preview_image: str
    document_path: str
    last_modified: str = None

templates_db = [
    {"id": 1, "title": "О представлении ", "preview_image": "/image2.png", "document_path": "/templates/template.docx", "last_modified": "5 минут назад"},
    {"id": 2, "title": "О представлении ", "preview_image": "/image2.png", "document_path": "/templates/template.docx", "last_modified": "5 минут назад"},
    {"id": 3, "title": "О представлении ", "preview_image": "/image2.png", "document_path": "/templates/template.docx", "last_modified": "5 минут назад"},
    {"id": 4, "title": "О представлении ", "preview_image": "/image2.png", "document_path": "/templates/template.docx", "last_modified": "5 минут назад"},
    {"id": 5, "title": "О представлении ", "preview_image": "/image2.png", "document_path": "/templates/template.docx", "last_modified": "5 минут назад"},
    {"id": 6, "title": "О представлении ", "preview_image": "/image2.png", "document_path": "/templates/template.docx", "last_modified": "5 минут назад"},
    {"id": 7, "title": "О представлении ", "preview_image": "/image2.png", "document_path": "/templates/template.docx", "last_modified": "5 минут назад"},
    {"id": 8, "title": "О представлении ", "preview_image": "/image2.png", "document_path": "/templates/template.docx", "last_modified": "5 минут назад"},
    {"id": 9, "title": "О представлении ", "preview_image": "/image2.png", "document_path": "/templates/template.docx", "last_modified": "5 минут назад"},
    {"id": 10, "title": "О представлении ", "preview_image": "/image2.png", "document_path": "/templates/template.docx", "last_modified": "5 минут назад"},
    {"id": 11, "title": "О представлении ", "preview_image": "/image2.png", "document_path": "/templates/template.docx", "last_modified": "5 минут назад"},
    {"id": 12, "title": "О представлении ", "preview_image": "/image2.png", "document_path": "/templates/template.docx", "last_modified": "5 минут назад"},
    {"id": 13, "title": "О представлении ", "preview_image": "/image2.png", "document_path": "/templates/template.docx", "last_modified": "5 минут назад"},
    {"id": 14, "title": "О представлении ", "preview_image": "/image2.png", "document_path": "/templates/template.docx", "last_modified": "5 минут назад"},
]

@app.get("/api/templates/recent", response_model=List[Template])
async def get_recent_templates(limit: int = 100):
    return templates_db[:limit]

@app.get("/api/templates/all", response_model=List[Template])
async def get_all_templates(skip: int = 0, limit: int = 100):
    return templates_db[skip : skip + limit]

@app.get("/api/templates/search")
async def search_templates(query: str):
    return [t for t in templates_db if query.lower() in t["title"].lower()]

@app.get("/images/{image_path:path}")
async def get_image(image_path: str):
    image_full_path = os.path.join("static", image_path)
    if not os.path.exists(image_full_path):
        raise HTTPException(status_code=404, detail="Image not found")
    return FileResponse(image_full_path)

@app.post("/api/process-document/")
async def process_document(request: Request):
    try:
        data = await request.json()
        docx_path = data.get("docx_path")
        print(docx_path)

        if not docx_path:
            raise HTTPException(status_code=400, detail="Не указан путь к документу")
        
        print(f"[1/6] Получен путь к DOCX: {docx_path}")

        full_docx_path = main(docx_path)
        print(f"[2/6] Обработанный путь: {full_docx_path}")

        """ if not os.path.exists(full_docx_path):
            error_msg = f"Файл {full_docx_path} не найден после обработки"
            print(f"[ERROR] {error_msg}")
            raise HTTPException(status_code=404, detail=error_msg)
        
        print(f"[3/6] DOCX файл существует: {os.path.getsize(full_docx_path)} байт")

        os.makedirs("converted_files", exist_ok=True)
        pdf_filename = os.path.basename(full_docx_path).replace('.docx', '.pdf')
        pdf_path = os.path.join("converted_files", pdf_filename)
        print(f"[4/6] Целевой PDF путь: {pdf_path}")

        try:
            print("[5/6] Начало конвертации...")
            docx2pdf.convert(full_docx_path, pdf_path)
            
            if not os.path.exists(pdf_path):
                raise Exception("PDF не появился после конвертации")
                
            print(f"[6/6] Конвертация успешна! Размер PDF: {os.path.getsize(pdf_path)} байт")
            
        except Exception as conv_error:
            error_msg = f"Ошибка конвертации: {str(conv_error)}"
            print(f"[ERROR] {error_msg}")
            raise HTTPException(status_code=500, detail=error_msg) """
        
        # 6. Возвращаем результат
        return JSONResponse({
            "full_docx_path": full_docx_path,
            "status": "success"
        })
        
    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"Непредвиденная ошибка: {str(e)}"
        print(f"[CRITICAL ERROR] {error_msg}")
        raise HTTPException(status_code=500, detail=error_msg)
    
@app.get("/onlyoffice/editor-config")
async def get_editor_config(file_name: str):
    file_name = os.path.basename(file_name)
    file_path = os.path.join("converted_files", file_name)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Файл не найден")

    file_url = f"http://host.docker.internal:8000/converted_files/{file_name}"
    print(file_url)
    # Уникальный ключ по имени файла (для OnlyOffice)
    doc_key = hashlib.md5((file_name + str(os.path.getmtime(file_path))).encode()).hexdigest()

    payload = {
        "document": {
            "fileType": "docx",
            "key": doc_key,
            "title": file_name,
            "url": file_url,
        },
        "editorConfig": {
            "callbackUrl": f"http://host.docker.internal:8000/onlyoffice/callback?file={file_name}",
            "mode": "edit",
            "user": {
                "id": "1",
                "name": "Ксения Гараева"
            }
        }
    }

    """ token = jwt.encode(config, JWT_SECRET, algorithm=JWT_ALGORITHM)
    config["token"] = token """

    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

    config = {
        **payload,
        "token": token
    }

    return JSONResponse(content=config)

@app.post("/onlyoffice/callback")
async def onlyoffice_callback(request: Request, file: str = Query(...)):
    body = await request.json()
    status = body.get("status")

    # Сохраняем файл только если статус 2 (закрыт) или 6 (форс сохранение)
    if status in [2, 6]:
        download_url = body.get("url")
        if not download_url:
            return JSONResponse({"error": "No download URL"}, status_code=400)

        save_path = os.path.join("converted_files", os.path.basename(file))
        print(save_path)

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(download_url) as resp:
                    if resp.status == 200:
                        with open(save_path, "wb") as f:
                            f.write(await resp.read())
                    else:
                        return JSONResponse({"error": "Failed to download edited file"}, status_code=500)

        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=500)

    return JSONResponse({"error": 0})

""" @app.post("/onlyoffice/callback")
async def onlyoffice_callback(request: Request, file: str):
    data = await request.json()
    print(f"[OnlyOffice Callback] Получены данные: {data}")

    # Статус 2 — документ готов к сохранению
    if data.get("status") == 2 and "url" in data:
        download_url = data["url"]
        try:
            response = requests.get(download_url)
            save_path = os.path.join("converted_files", file)
            with open(save_path, "wb") as f:
                f.write(response.content)
            print(f"[OnlyOffice Callback] Файл сохранён: {save_path}")
        except Exception as e:
            print(f"[OnlyOffice Callback] Ошибка при загрузке: {e}")
            raise HTTPException(status_code=500, detail="Не удалось сохранить изменения")
    
    return JSONResponse(content={"error": 0}) """

# Не рабочий вариант полностью пропадают стили при сохранении HTML -> DOCX
""" @app.post("/api/save-docx")
async def save_docx(request: Request):
    try:
        data = await request.json()
        html = data.get("html")
        original_path = data.get("original_path")

        if not html:
            return JSONResponse(status_code=400, content={"detail": "Пустой HTML"})

        soup = BeautifulSoup(html, "html.parser")
        plain_text = soup.get_text(separator="\n")

        doc = Document()
        for line in plain_text.splitlines():
            doc.add_paragraph(line)

        filename = os.path.basename(original_path or "edited.docx")
        save_path = os.path.join("converted_files", filename)
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        doc.save(save_path)

        print(f"[SAVE] Документ сохранён: {save_path}")
        return JSONResponse({"status": "saved", "path": save_path})
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": f"Ошибка сервера: {str(e)}"}) """