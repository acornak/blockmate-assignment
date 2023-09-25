"""Base test class for all tests."""
from datetime import datetime

import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519


def generate_token(expiry_time: datetime) -> str:
    """
    Generate a dummy JWT token for testing purposes.

    :param expiry_time: Expiration time of the token.

    :return: JWT token.
    """
    private_key = ed25519.Ed25519PrivateKey.generate()

    pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )

    payload = {"exp": expiry_time}

    return jwt.encode(payload, key=pem, algorithm="EdDSA")
