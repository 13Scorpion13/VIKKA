from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List
from bs4 import BeautifulSoup
from docx import Document
import os
import time
from pathlib import Path
import docx2pdf
from parser import main

app = FastAPI()

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

# Не рабочий вариант полностью пропадают стили при сохранении HTML -> DOCX
@app.post("/api/save-docx")
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
        return JSONResponse(status_code=500, content={"detail": f"Ошибка сервера: {str(e)}"})