from fastapi import Depends, HTTPException, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert, select, update, delete

from database import get_async_session
from models import notebook
from schemas import NotebookCreate, NotebookUpdate, NotebookRead

router = APIRouter(prefix="/notebook", tags=["Notebook"])

async def get_notebook_by_id(session: AsyncSession, notebook_id: int):
    query = select(notebook).where(notebook.c.id == notebook_id)
    result = await session.execute(query)
    return result.mappings().one_or_none()


@router.post("/", response_model=NotebookRead)
async def create_notebook(
    data: NotebookCreate,
    session: AsyncSession = Depends(get_async_session)
):
    try:
        query = insert(notebook).values(**data.model_dump()).returning(notebook.c.id)
        result = await session.execute(query)
        notebook_id = result.scalar_one()
        await session.commit()
        return await get_notebook_by_id(session, notebook_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Ошибка при создании ноутбука")


@router.get("/{notebook_id}", response_model=NotebookRead)
async def read_notebook(
    notebook_id: int,
    session: AsyncSession = Depends(get_async_session)
):
    db_item = await get_notebook_by_id(session, notebook_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Ноутбук не найден")
    return db_item


@router.get("/", response_model=list[NotebookRead])
async def read_all_notebooks(
    session: AsyncSession = Depends(get_async_session)
):
    query = select(notebook)
    result = await session.execute(query)
    return result.mappings().all()


@router.put("/{notebook_id}", response_model=NotebookRead)
async def update_notebook(
    notebook_id: int,
    data: NotebookUpdate,
    session: AsyncSession = Depends(get_async_session)
):
    db_item = await get_notebook_by_id(session, notebook_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Ноутбук не найден")

    try:
        query = (
            update(notebook)
            .where(notebook.c.id == notebook_id)
            .values(**{k: v for k, v in data.model_dump().items() if v is not None})
            .returning(notebook.c.id)
        )
        await session.execute(query)
        await session.commit()
        return await get_notebook_by_id(session, notebook_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Ошибка при обновлении ноутбука")


@router.delete("/{notebook_id}")
async def delete_notebook(
    notebook_id: int,
    session: AsyncSession = Depends(get_async_session)
):
    db_item = await get_notebook_by_id(session, notebook_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Ноутбук не найден")

    try:
        query = delete(notebook).where(notebook.c.id == notebook_id)
        await session.execute(query)
        await session.commit()
        return {"message": "Ноутбук успешно удалён"}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Ошибка при удалении ноутбука")