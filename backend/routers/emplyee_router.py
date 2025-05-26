from fastapi import Depends, HTTPException, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert, select, update, delete

from database import get_async_session
from models import employee, notebook
from schemas import EmployeeCreate, EmployeeUpdate, EmployeeRead
from db_utils import get_employee_by_id

router = APIRouter(prefix="/employee", tags=["Employee"])

""" async def get_employee_by_id(session: AsyncSession, emp_id: int):
    query = select(employee).where(employee.c.id == emp_id)
    result = await session.execute(query)
    return result.mappings().one_or_none() """


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


async def get_all_employees_with_notebook(session):
    query = (
        select(
            employee.c.id,
            employee.c.full_name,
            employee.c.position,
            notebook.c.notebooks_name,
            notebook.c.serial_number
        )
        .select_from(employee.join(notebook))
    )
    result = await session.execute(query)
    return result.mappings().all()

@router.get("/", response_model=list[EmployeeRead])
async def read_all_employees(
    session: AsyncSession = Depends(get_async_session)
):
    db_items = await get_all_employees_with_notebook(session)

    if not db_items:
        raise HTTPException(status_code=404, detail="Сотрудники не найдены")

    return [
        {
            "id": item.id,
            "full_name": item.full_name,
            "position": item.position,
            "notebook": f"{item.notebooks_name}, \n{item.serial_number}"
        }
        for item in db_items
    ]


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