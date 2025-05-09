from fastapi import Depends, HTTPException, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert, select, update, delete

from database import get_async_session
from models import faximili
from schemas import FaximiliCreate, FaximiliUpdate, FaximiliRead


router = APIRouter(prefix="/faximili", tags=["Faximili"])

async def get_faximili_by_id(session: AsyncSession, faximili_id: int):
    query = select(faximili).where(faximili.c.id == faximili_id)
    result = await session.execute(query)
    return result.mappings().one_or_none()

@router.post("/", response_model=FaximiliRead)
async def create_faximili(
    data: FaximiliCreate,
    session: AsyncSession = Depends(get_async_session)
):
    try:
        query = insert(faximili).values(**data.model_dump()).returning(faximili.c.id)
        result = await session.execute(query)
        faximili_id = result.scalar_one()
        await session.commit()
        return await get_faximili_by_id(session, faximili_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Ошибка при создании факсимиле")


@router.get("/{faximili_id}", response_model=FaximiliRead)
async def read_faximili(
    faximili_id: int,
    session: AsyncSession = Depends(get_async_session)
):
    db_item = await get_faximili_by_id(session, faximili_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Факсимиле не найдено")
    return db_item


@router.get("/", response_model=list[FaximiliRead])
async def read_all_faximili(
    session: AsyncSession = Depends(get_async_session)
):
    query = select(faximili)
    result = await session.execute(query)
    return result.mappings().all()


@router.put("/{faximili_id}", response_model=FaximiliRead)
async def update_faximili(
    faximili_id: int,
    data: FaximiliUpdate,
    session: AsyncSession = Depends(get_async_session)
):
    db_item = await get_faximili_by_id(session, faximili_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Факсимиле не найдено")

    try:
        query = (
            update(faximili)
            .where(faximili.c.id == faximili_id)
            .values(**{k: v for k, v in data.model_dump().items() if v is not None})
            .returning(faximili.c.id)
        )
        await session.execute(query)
        await session.commit()
        return await get_faximili_by_id(session, faximili_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Ошибка при обновлении факсимиле")


@router.delete("/{faximili_id}")
async def delete_faximili(
    faximili_id: int,
    session: AsyncSession = Depends(get_async_session)
):
    db_item = await get_faximili_by_id(session, faximili_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Факсимиле не найдено")

    try:
        query = delete(faximili).where(faximili.c.id == faximili_id)
        await session.execute(query)
        await session.commit()
        return {"message": "Факсимиле успешно удалено"}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Ошибка при удалении факсимиле")