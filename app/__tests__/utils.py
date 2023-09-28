"""
Utils for tests.

This module provides utilities for generating JWT tokens required
for testing various components of the application.

Components:
- generate_token: Function to generate a dummy JWT token with a given expiry time.

Key Dependencies:
- datetime for datetime operations
- jwt for generating JSON Web Tokens (JWT)
- ed25519 from cryptography.hazmat.primitives.asymmetric for generating Ed25519 private keys
- serialization from cryptography.hazmat.primitives for PEM encoding

Usage:
This function is meant to be used in the test suites to simulate authentic JWT tokens.

"""
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
