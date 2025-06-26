from typing import Any, Optional
from fastapi.responses import JSONResponse


class SuccessResponse(JSONResponse):
    def __init__(self, data: Any = None, msg: Optional[str] = None, status_code: int = 200):
        content = {
            "status": "success",
            "data": data,
            "message": msg
        }
        super().__init__(content=content, status_code=status_code)
class ErrorResponse(JSONResponse):
    def __init__(self, error: Optional[str] = None, msg: Optional[str] = None, status_code: int = 400):
        content = {
            "status": "error",
            "error": error,
            "message": msg
        }
        super().__init__(content=content, status_code=status_code)

