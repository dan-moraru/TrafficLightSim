import pytest
from signature_wrapper import generate_key_pair, sign, verify

# Test for key signing and verifying
@pytest.fixture
def key_pair():
    return generate_key_pair()

@pytest.fixture
def message():
    return b"My website is http://elc.github.io"

@pytest.fixture
def wrong_message():
    return b"My website is http://www.google.com"

def test_sign_and_verify(key_pair, message):
    private_key, public_key = key_pair
    signature = sign(message, private_key)
    verification_message = verify(signature, message, public_key)
    assert verification_message is True

def test_verify_wrong_message(key_pair, message, wrong_message):
    private_key, public_key = key_pair
    signature = sign(message, private_key)
    verification_message = verify(signature, wrong_message, public_key)
    assert verification_message is False

def test_verify_wrong_signature(key_pair, message, wrong_message):
    private_key, public_key = key_pair
    fake_private_key, _ = generate_key_pair()
    fake_signature = sign(wrong_message, fake_private_key)
    verification_message = verify(fake_signature, message, public_key)
    assert verification_message is False

def test_verify_success(key_pair, message):
    private_key, public_key = key_pair
    signature = sign(message, private_key)
    verification_message = verify(signature, message, public_key)
    assert verification_message is True