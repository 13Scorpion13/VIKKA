from fastapi import Depends, HTTPException, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert, select, update, delete

from database import get_async_session
from models import employee
from schemas import EmployeeCreate, EmployeeUpdate, EmployeeRead

router = APIRouter(prefix="/employee", tags=["Employee"])

async def get_employee_by_id(session: AsyncSession, emp_id: int):
    query = select(employee).where(employee.c.id == emp_id)
    result = await session.execute(query)
    return result.mappings().one_or_none()


@router.post("/", response_model=EmployeeRead)
async def create_employee(
    data: EmployeeCreate,
    session: AsyncSession = Depends(get_async_session)
):
    try:
        query = insert(employee).values(**data.model_dump()).returning(employee.c.id)
        result = await session.execute(query)
        emp_id = result.scalar_one()
        await session.commit()
        return await get_employee_by_id(session, emp_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Ошибка при создании сотрудника")


@router.get("/{emp_id}", response_model=EmployeeRead)
async def read_employee(
    emp_id: int,
    session: AsyncSession = Depends(get_async_session)
):
    db_item = await get_employee_by_id(session, emp_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Сотрудник не найден")
    return db_item


@router.get("/", response_model=list[EmployeeRead])
async def read_all_employees(
    session: AsyncSession = Depends(get_async_session)
):
    query = select(employee)
    result = await session.execute(query)
    return result.mappings().all()


@router.put("/{emp_id}", response_model=EmployeeRead)
async def update_employee(
    emp_id: int,
    data: EmployeeUpdate,
    session: AsyncSession = Depends(get_async_session)
):
    db_item = await get_employee_by_id(session, emp_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Сотрудник не найден")

    try:
        query = (
            update(employee)
            .where(employee.c.id == emp_id)
            .values(**{k: v for k, v in data.model_dump().items() if v is not None})
            .returning(employee.c.id)
        )
        await session.execute(query)
        await session.commit()
        return await get_employee_by_id(session, emp_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Ошибка при обновлении сотрудника")


@router.delete("/{emp_id}")
async def delete_employee(
    emp_id: int,
    session: AsyncSession = Depends(get_async_session)
):
    db_item = await get_employee_by_id(session, emp_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Сотрудник не найден")

    try:
        query = delete(employee).where(employee.c.id == emp_id)
        await session.execute(query)
        await session.commit()
        return {"message": "Сотрудник успешно удалён"}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Ошибка при удалении сотрудника")