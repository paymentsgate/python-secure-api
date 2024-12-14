from dataclasses import dataclass
from pydantic import BaseModel

@dataclass
class Request:
    method: str
    path: str
    content_type: str = 'application/json'
    headers: dict[str, str] | None = None
    body: dict | None = None
    noAuth: bool | None = False
    signature: bool | None = False


@dataclass
class Response:
    raw_body: bytes
    json: dict
    status_code: int

    @property
    def success(self) -> bool:
        return self.status_code < 400

    def cast(self, model: BaseModel, error: dict):
        if self.success:
            return model(**self.json)
        return error(self.json.get('error'), self.json.get('message'), self.json.get('data'), self.json.get('status'));
    
    def __str__(self) -> str:
       return self.raw_body.decode("utf-8")