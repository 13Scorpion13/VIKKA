from fastapi import Depends, HTTPException, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert, select, update, delete

from database import get_async_session
from models import letter_history
from schemas import LetterHistoryCreate, LetterHistoryUpdate, LetterHistoryRead

router = APIRouter(prefix="/letter_history", tags=["Letter_history"])

async def get_letter_history_by_id(session: AsyncSession, history_id: int):
    query = select(letter_history).where(letter_history.c.id == history_id)
    result = await session.execute(query)
    return result.mappings().one_or_none()


@router.post("/", response_model=LetterHistoryRead)
async def create_letter_history(
    data: LetterHistoryCreate,
    session: AsyncSession = Depends(get_async_session)
):
    try:
        query = insert(letter_history).values(**data.model_dump()).returning(letter_history.c.id)
        result = await session.execute(query)
        history_id = result.scalar_one()
        await session.commit()
        return await get_letter_history_by_id(session, history_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Ошибка при создании истории письма")


@router.get("/{history_id}", response_model=LetterHistoryRead)
async def read_letter_history(
    history_id: int,
    session: AsyncSession = Depends(get_async_session)
):
    db_item = await get_letter_history_by_id(session, history_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="История письма не найдена")
    return db_item


@router.get("/", response_model=list[LetterHistoryRead])
async def read_all_letter_history(
    session: AsyncSession = Depends(get_async_session)
):
    query = select(letter_history)
    result = await session.execute(query)
    return result.mappings().all()


@router.put("/{history_id}", response_model=LetterHistoryRead)
async def update_letter_history(
    history_id: int,
    data: LetterHistoryUpdate,
    session: AsyncSession = Depends(get_async_session)
):
    db_item = await get_letter_history_by_id(session, history_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="История письма не найдена")

    try:
        query = (
            update(letter_history)
            .where(letter_history.c.id == history_id)
            .values(**{k: v for k, v in data.model_dump().items() if v is not None})
            .returning(letter_history.c.id)
        )
        await session.execute(query)
        await session.commit()
        return await get_letter_history_by_id(session, history_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Ошибка при обновлении истории письма")


@router.delete("/{history_id}")
async def delete_letter_history(
    history_id: int,
    session: AsyncSession = Depends(get_async_session)
):
    db_item = await get_letter_history_by_id(session, history_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="История письма не найдена")

    try:
        query = delete(letter_history).where(letter_history.c.id == history_id)
        await session.execute(query)
        await session.commit()
        return {"message": "История письма успешно удалена"}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Ошибка при удалении истории письма")