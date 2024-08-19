import pytest
import time
from jwt_wrapper import authenticate, decode, check_expired

# Incorrect user or incorrect password
def test_incorrect_user_or_password():
    invalid_token = authenticate("admin", "incorrect_password")
    assert invalid_token is None

@pytest.fixture()
def test_authenticate():
    valid_token = authenticate("admin", "password")
    return valid_token
@pytest.fixture
def test_decode(test_authenticate):
    decoded = decode(test_authenticate)
    return decoded

# Decode and verify the JWT, and test the subject claim
def test_decode_subject(test_decode):
    assert "admin" == test_decode["sub"]

# Check the valid expiration time of the JWT
def test_valid_token_not_expired(test_decode):
    assert check_expired(test_decode["exp"]) is False

# Check the expiration time of the JWT
def test_valid_token_expired(test_decode):
    assert check_expired(test_decode["exp"]) is False
    time.sleep(1)  # to pass 0.5 seconds
    assert check_expired(test_decode["exp"]) is True

def test_expired(test_decode):
    time.sleep(1)  # to pass 0.5 seconds
    assert check_expired(test_decode["exp"]) is True
