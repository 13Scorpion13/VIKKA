from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List
from bs4 import BeautifulSoup
from docx import Document
import os
import re
from datetime import datetime
import time
from pathlib import Path
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
    
@app.post("/api/extract-fields")
async def extract_fields(request: Request):
    """Извлекает поля вида {field_name} из DOCX."""
    try:
        data = await request.json()
        docx_path = data.get("docx_path")
        
        if not docx_path:
            raise HTTPException(status_code=400, detail="Не указан путь к документу")
        
        doc = Document(docx_path)
        fields = set()
        
        # Ищем поля в тексте и таблицах
        for paragraph in doc.paragraphs:
            matches = re.findall(r"\{(\w+)\}", paragraph.text)
            fields.update(matches)
        
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    matches = re.findall(r"\{(\w+)\}", cell.text)
                    fields.update(matches)
        
        return {"fields": list(fields)}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при извлечении полей: {str(e)}")
    
@app.post("/api/replace-fields")
async def replace_fields(request: Request):
    """Заменяет {field_name} в DOCX на значения из запроса."""
    try:
        data = await request.json()
        docx_path = data.get("docx_path")
        fields_data = data.get("fields_data", {})
        
        if not docx_path:
            raise HTTPException(status_code=400, detail="Не указан путь к документу")
        
        doc = Document(docx_path)
        
        # Заменяем поля в тексте
        for paragraph in doc.paragraphs:
            for field, value in fields_data.items():
                if f"{{{field}}}" in paragraph.text:
                    paragraph.text = paragraph.text.replace(f"{{{field}}}", str(value))
        
        # Заменяем поля в таблицах
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    for field, value in fields_data.items():
                        if f"{{{field}}}" in cell.text:
                            cell.text = cell.text.replace(f"{{{field}}}", str(value))
        
        # Сохраняем новый файл
        output_path = f"converted_files/processed_{datetime.now().timestamp()}.docx"
        doc.save(output_path)
        
        return {"processed_docx_path": output_path}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при замене полей: {str(e)}")