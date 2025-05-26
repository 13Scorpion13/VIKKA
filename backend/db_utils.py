from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models import adressee, signer, employee

async def get_adressee_by_id(session: AsyncSession, adressee_id: int):
    query = select(adressee).where(adressee.c.id == adressee_id)
    result = await session.execute(query)
    return result.mappings().one_or_none()

async def get_signer_by_id(session: AsyncSession, signer_id: int):
    query = select(signer).where(signer.c.id == signer_id)
    result = await session.execute(query)
    return result.mappings().one_or_none()

async def get_employee_by_id(session: AsyncSession, emp_id: int):
    query = select(employee).where(employee.c.id == emp_id)
    result = await session.execute(query)
    return result.mappings().one_or_none()