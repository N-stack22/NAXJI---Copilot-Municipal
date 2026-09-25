from typing import Annotated

from pydantic import BaseModel, ConfigDict, StringConstraints


Texto = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class RequestModel(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)


class ResponseModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)
