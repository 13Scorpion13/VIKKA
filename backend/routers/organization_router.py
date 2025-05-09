from fastapi import Depends, HTTPException, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert, select, update, delete

from database import get_async_session
from models import organization
from schemas import OrganizationCreate, OrganizationUpdate, OrganizationRead

router = APIRouter(prefix="/organization", tags=["Organization"])

async def get_organization_by_id(session: AsyncSession, org_id: int):
    query = select(organization).where(organization.c.id == org_id)
    result = await session.execute(query)
    return result.mappings().one_or_none()


@router.post("/", response_model=OrganizationRead)
async def create_organization(
    data: OrganizationCreate,
    session: AsyncSession = Depends(get_async_session)
):
    try:
        query = insert(organization).values(**data.model_dump()).returning(organization.c.id)
        result = await session.execute(query)
        org_id = result.scalar_one()
        await session.commit()
        return await get_organization_by_id(session, org_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Ошибка при создании организации")


@router.get("/{org_id}", response_model=OrganizationRead)
async def read_organization(
    org_id: int,
    session: AsyncSession = Depends(get_async_session)
):
    db_item = await get_organization_by_id(session, org_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Организация не найдена")
    return db_item


@router.get("/", response_model=list[OrganizationRead])
async def read_all_organizations(
    session: AsyncSession = Depends(get_async_session)
):
    query = select(organization)
    result = await session.execute(query)
    return result.mappings().all()


@router.put("/{org_id}", response_model=OrganizationRead)
async def update_organization(
    org_id: int,
    data: OrganizationUpdate,
    session: AsyncSession = Depends(get_async_session)
):
    db_item = await get_organization_by_id(session, org_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Организация не найдена")

    try:
        query = (
            update(organization)
            .where(organization.c.id == org_id)
            .values(**{k: v for k, v in data.model_dump().items() if v is not None})
            .returning(organization.c.id)
        )
        await session.execute(query)
        await session.commit()
        return await get_organization_by_id(session, org_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Ошибка при обновлении организации")


@router.delete("/{org_id}")
async def delete_organization(
    org_id: int,
    session: AsyncSession = Depends(get_async_session)
):
    db_item = await get_organization_by_id(session, org_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Организация не найдена")

    try:
        query = delete(organization).where(organization.c.id == org_id)
        await session.execute(query)
        await session.commit()
        return {"message": "Организация успешно удалена"}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Ошибка при удалении организации")