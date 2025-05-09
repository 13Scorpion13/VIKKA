from fastapi import Depends, HTTPException, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert, select, update, delete

from database import get_async_session
from models import area
from schemas import AreaCreate, AreaUpdate, AreaRead

router = APIRouter(prefix="/area", tags=["Area"])

async def get_area_by_id(session: AsyncSession, area_id: int):
    query = select(area).where(area.c.id == area_id)
    result = await session.execute(query)
    return result.mappings().one_or_none()


@router.post("/", response_model=AreaRead)
async def create_area(
    data: AreaCreate,
    session: AsyncSession = Depends(get_async_session)
):
    try:
        query = insert(area).values(**data.model_dump()).returning(area.c.id)
        result = await session.execute(query)
        area_id = result.scalar_one()
        await session.commit()
        return await get_area_by_id(session, area_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Ошибка при создании области")


@router.get("/{area_id}", response_model=AreaRead)
async def read_area(
    area_id: int,
    session: AsyncSession = Depends(get_async_session)
):
    db_item = await get_area_by_id(session, area_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Область не найдена")
    return db_item


@router.get("/", response_model=list[AreaRead])
async def read_all_areas(
    session: AsyncSession = Depends(get_async_session)
):
    query = select(area)
    result = await session.execute(query)
    return result.mappings().all()


@router.put("/{area_id}", response_model=AreaRead)
async def update_area(
    area_id: int,
    data: AreaUpdate,
    session: AsyncSession = Depends(get_async_session)
):
    db_item = await get_area_by_id(session, area_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Область не найдена")

    try:
        query = (
            update(area)
            .where(area.c.id == area_id)
            .values(**{k: v for k, v in data.model_dump().items() if v is not None})
            .returning(area.c.id)
        )
        await session.execute(query)
        await session.commit()
        return await get_area_by_id(session, area_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Ошибка при обновлении области")


@router.delete("/{area_id}")
async def delete_area(
    area_id: int,
    session: AsyncSession = Depends(get_async_session)
):
    db_item = await get_area_by_id(session, area_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Область не найдена")

    try:
        query = delete(area).where(area.c.id == area_id)
        await session.execute(query)
        await session.commit()
        return {"message": "Область успешно удалена"}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Ошибка при удалении области")