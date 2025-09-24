import pytest
from app.schemas.user import UserCreate, UserLogin
from app.services.auth_service import register_user, login_user
from app.crud import user as user_crud


@pytest.mark.asyncio
async def test_register_user_success(test_db):
    user_data = UserCreate(
        name="Service User",
        email="service@example.com",
        password="servicepass"
    )
    result = await register_user(test_db, user_data)
    assert "user_id" in result
    assert result["message"].startswith("User registered successfully")


@pytest.mark.asyncio
async def test_register_user_existing_email(test_db, test_user):
    user_data = UserCreate(
        name=test_user.name,
        email=test_user.email,
        password="testpassword"
    )
    with pytest.raises(Exception):
        await register_user(test_db, user_data)


def test_login_user_success(test_db):
    user_data = UserCreate(
        name="Login Service",
        email="loginservice@example.com",
        password="loginpass"
    )
    
    user = user_crud.create_user(test_db, user_data)

    user.is_active = True
    user.is_verified = True
    test_db.commit()
    test_db.refresh(user)

    user_login = UserLogin(
        email="loginservice@example.com", password="loginpass"
    )
    token = login_user(test_db, user_login)

    assert token.token_type == "bearer"
    assert token.access_token is not None


def test_login_user_wrong_password(test_db):
    user_data = UserCreate(
        name="Wrong Password",
        email="wrongpass@example.com",
        password="correctpass"
    )
    user_crud.create_user(test_db, user_data)

    user_login = UserLogin(email="wrongpass@example.com", password="wrongpass")
    import pytest
    from fastapi import HTTPException
    with pytest.raises(HTTPException):
        login_user(test_db, user_login)
