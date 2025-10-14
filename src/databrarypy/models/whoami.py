"""Model for the /oauth2/test/ (whoami) endpoint response."""

from __future__ import annotations

from pydantic import BaseModel, Field


class WhoAmI(BaseModel):
    """Represents the response from /oauth2/test/.

    Supports both camelCase (server) and snake_case (client-normalized) inputs.
    Unknown fields are forbidden.
    """

    auth_method: str = Field(alias="authMethod")
    user: str = Field(alias="user")
    message: str = Field(alias="message")
    path: str = Field(alias="path")
    model_config = {
        "populate_by_name": True,
        "extra": "forbid",
    }
