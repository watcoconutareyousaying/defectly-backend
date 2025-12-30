from app.core.security import get_password_hash, verify_password, create_access_token, decode_token


def test_password_hashing():
    password = "mypassword"
    hashed = get_password_hash(password)
    assert verify_password(password, hashed)


def test_token_creation_and_decode():
    subject = "user@example.com"
    token = create_access_token(subject)
    decoded = decode_token(token)
    assert decoded == subject
