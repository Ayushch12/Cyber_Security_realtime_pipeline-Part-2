from pydantic import BaseModel


class IDSLogRequest(BaseModel):
    log_line: str
