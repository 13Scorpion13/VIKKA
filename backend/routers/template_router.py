from fastapi import Depends, HTTPException, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert, select, update, delete

from database import get_async_session
from models import template
from schemas import TemplateCreate, TemplateUpdate, TemplateRead

router = APIRouter(prefix="/template", tags=["Template"])

async def get_template_by_id(session: AsyncSession, template_id: int):
    query = select(template).where(template.c.id == template_id)
    result = await session.execute(query)
    return result.mappings().one_or_none()


@router.post("/", response_model=TemplateRead)
async def create_template(
    data: TemplateCreate,
    session: AsyncSession = Depends(get_async_session)
):
    try:
        query = insert(template).values(**data.model_dump()).returning(template.c.id)
        result = await session.execute(query)
        template_id = result.scalar_one()
        await session.commit()
        return await get_template_by_id(session, template_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при создании шаблона {e}")


@router.get("/{template_id}", response_model=TemplateRead)
async def read_template(
    template_id: int,
    session: AsyncSession = Depends(get_async_session)
):
    db_item = await get_template_by_id(session, template_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Шаблон не найден")
    return db_item


@router.get("/", response_model=list[TemplateRead])
async def read_all_templates(
    session: AsyncSession = Depends(get_async_session)
):
    query = select(template)
    result = await session.execute(query)
    return result.mappings().all()


@router.put("/{template_id}", response_model=TemplateRead)
async def update_template(
    template_id: int,
    data: TemplateUpdate,
    session: AsyncSession = Depends(get_async_session)
):
    db_item = await get_template_by_id(session, template_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Шаблон не найден")

    try:
        query = (
            update(template)
            .where(template.c.id == template_id)
            .values(**{k: v for k, v in data.model_dump().items() if v is not None})
            .returning(template.c.id)
        )
        await session.execute(query)
        await session.commit()
        return await get_template_by_id(session, template_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Ошибка при обновлении шаблона")


@router.delete("/{template_id}")
async def delete_template(
    template_id: int,
    session: AsyncSession = Depends(get_async_session)
):
    db_item = await get_template_by_id(session, template_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Шаблон не найден")

    try:
        query = delete(template).where(template.c.id == template_id)
        await session.execute(query)
        await session.commit()
        return {"message": "Шаблон успешно удалён"}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Ошибка при удалении шаблона")