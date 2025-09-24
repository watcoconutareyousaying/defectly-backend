from app.crud import user as user_crud
from app.schemas.user import UserCreate


def test_create_user(test_db):
    user_data = UserCreate(
        name="CRUD User",
        email="cruduser@example.com",
        password="crudpass"
    )
    user = user_crud.create_user(test_db, user_data)
    assert user.id is not None
    assert user.email == "cruduser@example.com"


def test_authenticate_user_success(test_db):
    user_data = UserCreate(
        name="Auth User",
        email="authuser@example.com",
        password="authpass"
    )
    user_crud.create_user(test_db, user_data)
    authenticated = user_crud.authenticate_user(
        test_db, "authuser@example.com", "authpass")
    assert authenticated is not None
    assert authenticated.email == "authuser@example.com"


def test_authenticate_user_fail(test_db):
    authenticated = user_crud.authenticate_user(
        test_db, "nonexistent@example.com", "nopass")
    assert authenticated is None
