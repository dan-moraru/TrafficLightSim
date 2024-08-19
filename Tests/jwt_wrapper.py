import jwt
import datetime

# Helper methods
SECRET = "my-secret"

def authenticate(username, password):
    if username == "admin" and password == "password":
        expire_on = datetime.datetime.utcnow() + datetime.timedelta(seconds=0.5)
        payload = {"sub": "admin", "exp": expire_on.timestamp()}
        token = jwt.encode(payload, SECRET, algorithm="HS256")
        return token
    else:
        return None

def decode(valid_token):
    decoded = jwt.decode(valid_token, SECRET, verify=True, algorithms=["HS256"])
    return decoded

def check_expired(expire_on):
    return datetime.datetime.utcnow().timestamp() > expire_on
