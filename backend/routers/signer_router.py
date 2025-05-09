from fastapi import Depends, HTTPException, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert, select, update, delete

from database import get_async_session
from models import signer
from schemas import SignerCreate, SignerUpdate, SignerRead

router = APIRouter(prefix="/signer", tags=["Signer"])

async def get_signer_by_id(session: AsyncSession, signer_id: int):
    query = select(signer).where(signer.c.id == signer_id)
    result = await session.execute(query)
    return result.mappings().one_or_none()


@router.post("/", response_model=SignerRead)
async def create_signer(
    data: SignerCreate,
    session: AsyncSession = Depends(get_async_session)
):
    try:
        query = insert(signer).values(**data.model_dump()).returning(signer.c.id)
        result = await session.execute(query)
        signer_id = result.scalar_one()
        await session.commit()
        return await get_signer_by_id(session, signer_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Ошибка при создании подписанта")


@router.get("/{signer_id}", response_model=SignerRead)
async def read_signer(
    signer_id: int,
    session: AsyncSession = Depends(get_async_session)
):
    db_item = await get_signer_by_id(session, signer_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Подписант не найден")
    return db_item


@router.get("/", response_model=list[SignerRead])
async def read_all_signers(
    session: AsyncSession = Depends(get_async_session)
):
    query = select(signer)
    result = await session.execute(query)
    return result.mappings().all()


@router.put("/{signer_id}", response_model=SignerRead)
async def update_signer(
    signer_id: int,
    data: SignerUpdate,
    session: AsyncSession = Depends(get_async_session)
):
    db_item = await get_signer_by_id(session, signer_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Подписант не найден")

    try:
        query = (
            update(signer)
            .where(signer.c.id == signer_id)
            .values(**{k: v for k, v in data.model_dump().items() if v is not None})
            .returning(signer.c.id)
        )
        await session.execute(query)
        await session.commit()
        return await get_signer_by_id(session, signer_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Ошибка при обновлении подписанта")


@router.delete("/{signer_id}")
async def delete_signer(
    signer_id: int,
    session: AsyncSession = Depends(get_async_session)
):
    db_item = await get_signer_by_id(session, signer_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Подписант не найден")

    try:
        query = delete(signer).where(signer.c.id == signer_id)
        await session.execute(query)
        await session.commit()
        return {"message": "Подписант успешно удалён"}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Ошибка при удалении подписанта")