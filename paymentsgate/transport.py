from dataclasses import dataclass
from pydantic import BaseModel

class Request(BaseModel):
    method: str
    path: str
    content_type: str = 'application/json'
    headers: dict[str, str] | None = None
    body: dict | None = None
    noAuth: bool | None = False
    signature: bool | None = False

class Response(BaseModel):
    raw_body: bytes
    json_body: dict
    status_code: int

    @property
    def success(self) -> bool:
        return self.status_code < 400

    def cast(self, model: BaseModel, error: dict):
        if self.success:
            return model(**self.json_body)
        return error(self.json_body.get('error'), self.json_body.get('message'), self.json_body.get('data'), self.json_body.get('status'));
    
    def __str__(self) -> str:
       return self.raw_body.decode("utf-8")