from datetime import datetime
import os
import re
import httpx
from typing import List
from docx import Document
from fastapi import Depends, HTTPException, APIRouter, Request
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert, select, update, delete
from parser import main
from database import get_async_session
from models import template, letter_history
from schemas import TemplateCreate, TemplateUpdate, TemplateRead
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

router = APIRouter(prefix="/api", tags=["api"])

templates_db = [
    {
        "id": 1,
        "title": "О представлении документации",
        "preview_image": "/image2.png",
        "document_path": "/templates/Письмо о представлении документации.docx",
        "form_type": "full",
        "last_modified": "5 минут назад"
    },
    {
        "id": 2,
        "title": "Письмо о допуске ",
        "preview_image": "/image2.png",
        "document_path": "/templates/Письмо о допуске.docx",
        "form_type": "minimal",
        "last_modified": "5 минут назад"
    }
]

@router.get("/templates/recent", response_model=List[TemplateRead])
async def get_recent_templates(limit: int = 100, session: AsyncSession = Depends(get_async_session)):
    query = select(template).limit(limit)
    result = await session.execute(query)
    
    # Получаем список словарей
    rows = result.mappings().all()

    transformed = []
    transformed = [
        dict(row) | {"last_modified": row["last_modified"].strftime("%Y-%m-%d")}
        for row in rows
    ]

    # transformed = [
    #     {
    #         "id": row.id,
    #         "title": row.title,
    #         "preview_image": row.preview_image,
    #         "document_path": row.document_path,
    #         "last_modified": humanize.naturaltime(datetime.now() - row.last_modified),
    #         "form_type": row.form_type
    #     }
    #     for row in rows
    # ]

    return transformed[: limit]

@router.get("/templates/all", response_model=List[TemplateRead])
async def get_all_templates(
    skip: int = 0,
    limit: int = 100,
    session: AsyncSession = Depends(get_async_session)
):
    query = select(template).limit(limit)
    result = await session.execute(query)
    
    # Получаем список словарей
    rows = result.mappings().all()

    # Преобразуем last_modified в нужный формат
    transformed = [
        dict(row) | {"last_modified": row["last_modified"].strftime("%Y-%m-%d")}
        for row in rows
    ]
    return transformed

    # return templates_db[skip : skip + limit]

@router.get("/templates/search")
async def search_templates(query: str):
    return [t for t in templates_db if query.lower() in t["title"].lower()]

@router.post("/process-document/")
async def process_document(request: Request):
    try:
        data = await request.json()
        print("Полученные данные:", data)

        recipient = data.get("recipient")
        signer = data.get("signer")
        docx_path = data.get("docx_path")

        if not all([docx_path, recipient, signer]):
            raise HTTPException(status_code=400, detail="Обязательные поля отсутствуют")
        
        template = next((t for t in templates_db if t["document_path"] == docx_path), None)
        form_type = template.get("form_type") if template else "full"

        if form_type == "full":
            contract_number = data.get("contract_number")
            contract_date = data.get("contract_date")
            pdf_folder_path = data.get("pdf_folder_path")
            
            if not all([contract_number, contract_date, pdf_folder_path]):
                raise HTTPException(status_code=400, detail="Не заполнены обязательные поля для полной формы")
        
        full_docx_path = main(
            docx_path=data["docx_path"],
            recipient=data["recipient"],
            signer=data["signer"],
            contract_number=data.get("contract_number"),
            contract_date=data.get("contract_date"),
            pdf_folder_path=data.get("pdf_folder_path")
        )
        print(f"[2/6] Обработанный путь: {full_docx_path}")
        
        
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
    
@router.post("/extract-fields")
async def extract_fields(request: Request):
    """Извлекает поля вида {field_name} из DOCX."""
    try:
        data = await request.json()
        docx_path = data.get("docx_path")
        
        if not docx_path:
            raise HTTPException(status_code=400, detail="Не указан путь к документу")
        
        doc = Document(docx_path)
        fields = set()
        
        
        for paragraph in doc.paragraphs:
            fields.update(re.findall(r"\{(\w+)\}", paragraph.text))
    
        for section in doc.sections:
            for paragraph in section.header.paragraphs:
                fields.update(re.findall(r"\{(\w+)\}", paragraph.text))
            for paragraph in section.footer.paragraphs:
                fields.update(re.findall(r"\{(\w+)\}", paragraph.text))
        
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    matches = re.findall(r"\{(\w+)\}", cell.text)
                    fields.update(matches)

        print(fields)
        
        return {"fields": list(fields)}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при извлечении полей: {str(e)}")
    
@router.post("/replace-fields")
async def replace_fields(request: Request):
    try:
        data = await request.json()
        docx_path = data.get("docx_path")
        print(f"Путь к файлу для сохранения: {docx_path}")
        fields_data = data.get("fields_data", {})
        
        if not docx_path:
            raise HTTPException(status_code=400, detail="Не указан путь к документу")
        
        if not os.path.exists(docx_path):
            raise HTTPException(status_code=404, detail="Файл не найден")
        
        doc = Document(docx_path)
        

        for paragraph in doc.paragraphs:
            for field, value in fields_data.items():
                if f"{{{field}}}" in paragraph.text:
                    paragraph.text = paragraph.text.replace(f"{{{field}}}", str(value))
        
        
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    for field, value in fields_data.items():
                        if f"{{{field}}}" in cell.text:
                            cell.text = cell.text.replace(f"{{{field}}}", str(value))
                            for paragraph in cell.paragraphs:
                                paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
                                for run in paragraph.runs:
                                    run.font.italic = True
        
        doc.save(docx_path)
        # print(int(data.get("user_id")), int(data.get("templateID")), docx_path, datetime.now().isoformat(), sep='\n')
        try:
            async with httpx.AsyncClient() as client:
                await client.post(
                    "http://localhost:8000/letter_history/",
                    json={
                        "user_id": data.get("user_id"),
                        "signer_id": 1,
                        "template_id": int(data.get("templateID")),
                        "file_path": docx_path,
                        "adressee_id": 1
                    }
                )
        except Exception as e:
            print(f"ERROR!!! {e}")
        return {"status": "success", "message": "Файл успешно обновлен", "file_path": docx_path}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при замене полей: {str(e)}")
    
@router.post("/add-table-row")
async def add_table_row(request: Request):
    data = await request.json()
    doc = Document(data["docx_path"])
    table = doc.tables[data["table_index"]]
    
    row_number = len(table.rows)
    new_row = table.add_row()
    
    if len(new_row.cells) >= 4:
        new_row.cells[0].text = str(row_number)
        new_row.cells[1].text = "{engineer_full_name}"
        new_row.cells[2].text = "{engineer_notebook}"
        new_row.cells[3].text = "{areas_name}"
        
        for cell in new_row.cells:
            for paragraph in cell.paragraphs:
                paragraph.paragraph_format.space_after = Pt(0)
                paragraph.paragraph_format.line_spacing = Pt(40)
                paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    doc.save(data["docx_path"])
    return {"status": "success", "file_path": data["docx_path"]}

@router.get("/engineers")
async def get_engineers():
    engineers = [
        {"full_name": "Иванов И.И.", "notebook": "Lenovo X1"},
        {"full_name": "Петров П.П.", "notebook": "Dell XPS"},
        {"full_name": "Сидоров С.С.", "notebook": "MacBook Pro"}
    ]
    return {"engineers": engineers}

@router.get("/areas")
async def get_areas():
    areas = ["Зона A", "Зона B", "Зона C", "Зона D"]
    return {"areas": areas}