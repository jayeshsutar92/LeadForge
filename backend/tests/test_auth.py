import pytest
from app.core.security import verify_password, get_password_hash, create_access_token

def test_password_hashing():
    password = "supersecretpassword123!"
    hashed = get_password_hash(password)
    assert hashed != password
    assert verify_password(password, hashed)
    assert not verify_password("wrongpassword", hashed)

def test_access_token_creation():
    subject = "user-uuid-1234"
    token = create_access_token(subject=subject, expires_delta=None)
    assert isinstance(token, str)
    assert len(token) > 0
