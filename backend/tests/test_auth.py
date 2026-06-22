import pytest
from app.security import hash_password, verify_password, create_access_token, decode_token, encrypt_api_key, decrypt_api_key


def test_password_hashing():
    pw = "testpassword123"
    hashed = hash_password(pw)
    assert hashed != pw
    assert verify_password(pw, hashed) is True
    assert verify_password("wrong", hashed) is False


def test_jwt_token():
    data = {"sub": "user-id-123"}
    token = create_access_token(data)
    payload = decode_token(token)
    assert payload is not None
    assert payload["sub"] == "user-id-123"
    assert payload["type"] == "access"
    assert "exp" in payload


def test_fernet_encryption():
    api_key = "sk-xxxxxxxxxxxxxxxxxxxx"
    encrypted = encrypt_api_key(api_key)
    assert encrypted != api_key
    decrypted = decrypt_api_key(encrypted)
    assert decrypted == api_key
