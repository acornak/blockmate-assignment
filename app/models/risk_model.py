"""
Model for the response from the risk endpoint.

This module contains the data models used for parsing
the risk details response from the Blockmate API.

Components:
- OwnCategory: Models the 'own_categories' and 'source_of_funds_categories'
  field in the risk details response.
- Details: Models the 'details' field, which encapsulates both 'own_categories'
  and 'source_of_funds_categories'.
- RiskDetailsResponse: Root model for parsing the entire risk details response.

Key Considerations:
- Uses Pydantic for data validation and serialization.
- Designed to closely map the JSON structure of the Blockmate API's response.

Dependencies:
- pydantic.BaseModel for data modeling and validation.

"""
from pydantic import BaseModel


class OwnCategory(BaseModel):
    """
    Data model for 'own_categories' and 'source_of_funds_categories' fields.

    :param address: Ethereum address.
    :param name: Name associated with the Ethereum address.
    :param category_name: Category name related to the address.
    :param risk: Risk score associated with the address.
    """

    address: str
    name: str
    category_name: str
    risk: int


class Details(BaseModel):
    """
    Data model for 'details' field in RiskDetailsResponse.

    :param own_categories: List of categories owned by the address.
    :param source_of_funds_categories: List of categories from source of funds.
    """

    own_categories: list[OwnCategory]
    source_of_funds_categories: list[OwnCategory]


class RiskDetailsResponse(BaseModel):
    """
    Root data model for parsing the risk details response.

    :param case_id: Case ID.
    :param request_datetime: Request timestamp.
    :param response_datetime: Response timestamp.
    :param chain: Blockchain chain (e.g., ETH).
    :param address: Ethereum address being checked.
    :param name: Name associated with the address.
    :param category_name: General category name.
    :param risk: General risk score.
    :param details: Additional details, including categories.
    """

    case_id: str
    request_datetime: str
    response_datetime: str
    chain: str
    address: str
    name: str
    category_name: str
    risk: int
    details: Details
