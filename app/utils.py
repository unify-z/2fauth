from typing import Callable
from app.responses import ErrorResponse
from functools import wraps
import jwt
from config.config_manager import config_manager
import time
from loguru import logger
from fastapi import Request,Response
from app.totp import NewTOTPConfig
import re
from urllib.parse import unquote, parse_qs

def encode_jwt(payload: dict, secret: str = str(config_manager.get("jwt.secret")), algorithm: str = "HS256",exp: int = int(time.time()) + 60 * 60) -> str:
    payload['exp'] = exp
    return jwt.encode(payload, secret, algorithm=algorithm)

def decode_jwt(token: str, secret: str = str(config_manager.get("jwt.secret")), algorithms: list = ["HS256"]) -> dict:
    return jwt.decode(token, secret, algorithms=algorithms)

def log_request(request: Request, response: Response):
    logger.info(f"[http] {request.client.host} {request.method} {response.status_code} {request.url.path}") # type: ignore

def parse_otpauth_url(input: str,user_id: int | str):
    if not input.startswith("otpauth://"):
        raise Exception("Url must startswith 'otpauth://'.")
    match = re.match(r"^otpauth://totp/([^:]+):([^?]+)\?(.+)$", input)
    if not match:
        raise Exception()
    account = match.group(2)
    params = parse_qs(match.group(3))
    secret = params.get("secret",[""])[0]
    issuer = params.get("issuer",[""])[0]
    return NewTOTPConfig(
        messages=[issuer,account],
        secret=secret,
        user_id=user_id
        )
    

    
    