"""Model for the check endpoint."""
from pydantic import BaseModel


class CheckEndpointResponse(BaseModel):
    """Model for the check endpoint."""

    category_names: list[str]
