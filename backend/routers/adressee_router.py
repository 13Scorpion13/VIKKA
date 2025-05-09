from fastapi import Depends, HTTPException, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert, select, update, delete

from database import get_async_session
from models import adressee
from schemas import AdresseeCreate, AdresseeUpdate, AdresseeRead

router = APIRouter(prefix="/adressee", tags=["Adressee"])


async def get_adressee_by_id(session: AsyncSession, adressee_id: int):
    query = select(adressee).where(adressee.c.id == adressee_id)
    result = await session.execute(query)
    return result.mappings().one_or_none()

@router.post("/", response_model=AdresseeRead)
async def create_adressee(
    data: AdresseeCreate,
    session: AsyncSession = Depends(get_async_session)
):
    try:
        query = (
            insert(adressee)
            .values(**data.model_dump())
            .returning(adressee.c.id)
        )
        result = await session.execute(query)
        adressee_id = result.scalar_one()
        await session.commit()
        return await get_adressee_by_id(session, adressee_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Ошибка при создании адресата")


@router.get("/{adressee_id}", response_model=AdresseeRead)
async def read_adressee(
    adressee_id: int,
    session: AsyncSession = Depends(get_async_session)
):
    db_item = await get_adressee_by_id(session, adressee_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Адресат не найден")
    return db_item


@router.get("/", response_model=list[AdresseeRead])
async def read_all_adressee(
    session: AsyncSession = Depends(get_async_session)
):
    query = select(adressee)
    result = await session.execute(query)
    return result.mappings().all()


@router.put("/{adressee_id}", response_model=AdresseeRead)
async def update_adressee(
    adressee_id: int,
    data: AdresseeUpdate,
    session: AsyncSession = Depends(get_async_session)
):
    db_item = await get_adressee_by_id(session, adressee_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Адресат не найден")

    try:
        query = (
            update(adressee)
            .where(adressee.c.id == adressee_id)
            .values(**{k: v for k, v in data.model_dump().items() if v is not None})
            .returning(adressee.c.id)
        )
        await session.execute(query)
        await session.commit()
        return await get_adressee_by_id(session, adressee_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Ошибка при обновлении адресата")


@router.delete("/{adressee_id}")
async def delete_adressee(
    adressee_id: int,
    session: AsyncSession = Depends(get_async_session)
):
    db_item = await get_adressee_by_id(session, adressee_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Адресат не найден")

    try:
        query = delete(adressee).where(adressee.c.id == adressee_id)
        await session.execute(query)
        await session.commit()
        return {"message": "Адресат успешно удалён"}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Ошибка при удалении адресата")