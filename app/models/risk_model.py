"""Model for the response from the risk endpoint."""
from pydantic import BaseModel


class OwnCategory(BaseModel):
    """Model for the own_categories and source_of_funds_categories."""

    address: str
    name: str
    category_name: str
    risk: int


class Details(BaseModel):
    """Model for details field in RiskDetailsResponse."""

    own_categories: list[OwnCategory]
    source_of_funds_categories: list[OwnCategory]


class RiskDetailsResponse(BaseModel):
    """Model for the response from the risk endpoint."""

    case_id: str
    request_datetime: str
    response_datetime: str
    chain: str
    address: str
    name: str
    category_name: str
    risk: int
    details: Details
