# generate pem files
from pathlib import Path
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa   

def generate_keys():
    global public_key
    # create private key
    key_size = 2048  # Should be at least 2048
    private_key = rsa.generate_private_key(
        public_exponent=65537,  # Do not change
        key_size=key_size,
    )
    # create public key
    public_key = private_key.public_key()

    #######Storing private key
    password = b"my secret"
    key_pem_bytes = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,  # PEM Format is specified
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.BestAvailableEncryption(password),
    )
    key_pem_path = Path("Keys/key.pem")
    key_pem_path.write_bytes(key_pem_bytes)
    ###### Storing public key
    public_pem_bytes = public_key.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    public_pem_path = Path("Keys/public.pem")
    public_pem_path.write_bytes(public_pem_bytes)

generate_keys()