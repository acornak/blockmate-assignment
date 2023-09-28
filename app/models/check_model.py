"""
Model for the check endpoint.

This module contains the data model used for serializing
the response of the /check endpoint in the API.

Components:
- CheckEndpointResponse: Data model for the API response.
  Contains a list of deduplicated category names.

Key Considerations:
- Uses Pydantic for data validation and serialization.

Dependencies:
- pydantic.BaseModel for data modeling and validation.

"""
from pydantic import BaseModel


class CheckEndpointResponse(BaseModel):
    """
    Data model for the /check endpoint API response.

    Potential TODO: add request ID for logging purposes.


    :param category_names: List of deduplicated category names.
    """

    category_names: list[str]
