import bcrypt
from fastapi import Depends, HTTPException, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert, select, update, delete

from database import get_async_session
from models import user
from schemas import UserCreate, UserUpdate, UserRead, LoginRequest

router = APIRouter(prefix="/users", tags=["Users"])

async def get_user_by_id(session: AsyncSession, user_id: int):
    query = select(user).where(user.c.id == user_id)
    result = await session.execute(query)
    return result.mappings().one_or_none()

@router.get("/{user_id}", response_model=UserRead)
async def read_user(
    user_id: int,
    session: AsyncSession = Depends(get_async_session)
):
    """
    Получение информации о пользователе по ID
    """
    db_user = await get_user_by_id(session, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return db_user

@router.get("/", response_model=list[UserRead])
async def read_all_users(
    session: AsyncSession = Depends(get_async_session)
):
    """
    Получение списка всех пользователей
    """
    query = select(user)
    result = await session.execute(query)
    return result.mappings().all()

@router.post("/register", response_model=UserRead)
async def register_user(
    user_data: UserCreate,
    session: AsyncSession = Depends(get_async_session)
):
    """
    Регистрация нового пользователя
    
    Args:
        user_data (UserCreate): Данные пользователя из формы
    Returns:
        dict: Созданный пользователь
    Raises:
        HTTPException: Если пользователь с таким email или login уже существует
    """

    try:
        existing_user_query = user.select().where(
            (user.c.email == user_data.email) | (user.c.user_number == user_data.user_number)
        )
        result = await session.execute(existing_user_query)
        existing_user = result.mappings().first()

        if existing_user:
            raise HTTPException(status_code=400, detail="Пользователь с таким email или логином уже существует")

        hashed_pw = hash_password(user_data.password)

        query = (
            insert(user)
            .values(
                user_number=user_data.user_number,
                full_name=user_data.full_name,
                email=user_data.email,
                phone_number=user_data.phone_number,
                password=hashed_pw
            )
            .returning(user.c.id)
        )

        result = await session.execute(query)
        new_user_id = result.scalar_one()
        await session.commit()

        new_user = await get_user_by_id(session, new_user_id)
        return new_user

    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail="Ошибка при регистрации")

async def get_user_by_id(session: AsyncSession, user_id: int):
    query = user.select().where(user.c.id == user_id)
    result = await session.execute(query)
    return result.mappings().one_or_none()

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())

async def authenticate_user(session: AsyncSession, login: str, password: str):
    query = select(user).where(
        (user.c.email == login) | (user.c.user_number == login)
    )
    result = await session.execute(query)
    db_user = result.mappings().one_or_none()

    if not db_user or not verify_password(password, db_user["password"]):
        raise HTTPException(status_code=401, detail="Неверный логин или пароль")

    return dict(db_user)

@router.post("/login")
async def login(login_data: LoginRequest, session: AsyncSession = Depends(get_async_session)):
    user = await authenticate_user(session, login_data.login, login_data.password)
    return {
        "message": "Авторизация успешна",
        "user": UserRead(**user).model_dump()
    }

@router.delete("/{user_id}")
async def delete_signer(
    user_id: int,
    session: AsyncSession = Depends(get_async_session)
):
    db_item = await get_user_by_id(session, user_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    try:
        query = delete(user).where(user.c.id == user_id)
        await session.execute(query)
        await session.commit()
        return {"message": "Пользователь успешно удалён"}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Ошибка при удалении пользователя")

@router.put("/{user_id}", response_model=UserUpdate)
async def update_adressee(
    user_id: int,
    data: UserUpdate,
    session: AsyncSession = Depends(get_async_session)
):
    db_item = await get_user_by_id(session, user_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    try:
        query = (
            update(user)
            .where(user.c.id == user_id)
            .values(**{k: v for k, v in data.model_dump().items() if v is not None})
            .returning(user.c.id)
        )
        await session.execute(query)
        await session.commit()
        return await get_user_by_id(session, user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Ошибка при обновлении пользователя")