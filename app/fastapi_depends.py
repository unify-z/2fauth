from fastapi import Request,HTTPException
from . import utils
import time

async def verify_token(reuqest: Request):
    token = reuqest.cookies.get("_auth")
    if not token:
        raise HTTPException(status_code=401, detail="Authentication token is required")
    try:
        payload = utils.decode_jwt(token)
        if payload.get("exp", 0) < int(time.time()):
            raise HTTPException(status_code=401, detail="Token has expired")
        required_permission = getattr(reuqest.scope.get("endpoint"), "required_permission", 0)
        if payload.get("permission", 0) < required_permission:
            raise HTTPException(status_code=403, detail="operation not permitted")
        return payload
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=401, detail=type(e).__name__)
    
    

def require_permission(permission: int):
    def decorator(func):
        setattr(func, "required_permission", permission)
        return func
    return decorator