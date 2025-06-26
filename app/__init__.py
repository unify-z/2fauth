from dataclasses import dataclass
import os
from fastapi import FastAPI,APIRouter, Request,Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from loguru import logger
from .responses import SuccessResponse, ErrorResponse
from database_clients.base import get_database_client
from config.config_manager import config_manager
from .totp import TOTPClient, TOTPConfig
from pydantic import BaseModel
from .user_manager import UserManager
from . import utils
from typing import Optional
import uvicorn
from .fastapi_depends import verify_token,require_permission
import traceback

app = FastAPI()
AUTH_ROUTER = APIRouter(prefix="/api/user")
TOTP_ROUTER = APIRouter(prefix="/api/totp")
DATABASE_CLIENT = get_database_client(str(config_manager.get("database.type")),db_path=config_manager.get("database.path"))
USER_DATABASE_CLIENT = get_database_client(str(config_manager.get("database.type")),db_path=config_manager.get("database.path"),table_name="users")
USER_CLIENT = UserManager(USER_DATABASE_CLIENT)
TOTP_CLIENT = TOTPClient(DATABASE_CLIENT)

app.mount("/assets", StaticFiles(directory="frontend/dist/assets"), name="assets")

@app.exception_handler(Exception)
async def exceptions_handler(request: Request, err: Exception):
    return ErrorResponse(error=f"{type(err).__name__ }: {str(err)}",msg="Internal server error",status_code=500)

@app.middleware("http")
async def spa_router(request: Request, call_next):
    path = request.url.path
    if path.startswith("/api") or path.startswith("/assets") or "." in path:
        return await call_next(request)
    return FileResponse("frontend/dist/index.html")

@dataclass
class WebServerConfig:
    host: str
    port: int
    enable_access_log: bool = True
    uvicorn_log_level: str = "critical"

class WebServer:
    def __init__(self, config: WebServerConfig):
        self.config = config
        self.app = app
        self.app.include_router(AUTH_ROUTER)
        self.app.include_router(TOTP_ROUTER)
        if self.config.enable_access_log:
            @self.app.middleware("http")
            async def log_requests(request: Request, call_next):
                response = await call_next(request)
                utils.log_request(request, response)
                return response
        if config_manager.get("cors.enabled", True):
            self.app.add_middleware(
                CORSMiddleware,
                allow_origins=config_manager.get("cors.allow_origins", ["*"]), # type: ignore
                allow_credentials=True,
                allow_methods=["*"],
                allow_headers=["*"],
            )
        

        

    def run(self):
        logger.info(f"Server linten {self.config.host}:{self.config.port}")
        uvicorn.run(self.app, host=self.config.host, port=self.config.port,access_log=False,log_level=self.config.uvicorn_log_level)



class RegisterRequest(BaseModel):
    username: str
    password: str



@AUTH_ROUTER.post("/register")
def register_user(request: RegisterRequest):
    if config_manager.get("auth.enable_registration", True) is False:
        return ErrorResponse(msg="注册功能已被禁用")
    USER_CLIENT.add_user(request.username,request.password)
    return SuccessResponse()

class LoginRequest(BaseModel):
    username: str
    password: str


@AUTH_ROUTER.post("/login")
def login(request: LoginRequest,req: Request):
    u = USER_CLIENT.get_user(request.username)
    user_salt = u.password_hash.split(":")[0]
    v_result = USER_CLIENT.verify_password(request.username,request.password,user_salt)
    if not v_result:
        return ErrorResponse(msg="账号或密码无效")
    resp = SuccessResponse(msg="登陆成功")
    resp.set_cookie(key="_auth",value=utils.encode_jwt(payload={
        "uid": u.user_id,
        "username": request.username,
        "permission": u.permission
    })) 
    return resp

 
@AUTH_ROUTER.get("/get_user")
def get_user(payload: dict = Depends(verify_token)):
    username = payload.get("username","")
    user = USER_CLIENT.get_user(username)
    return SuccessResponse(data={
        "user_id": user.user_id,
        "username": user.username,
        "permission": user.permission
    })

class EditUserRequest(BaseModel):
    password: Optional[str] = None
    permission: Optional[int] = None


@AUTH_ROUTER.patch("/edit/{user_id}")
@require_permission(1)
def edit_user(user_id: int, request: EditUserRequest,depends: dict = Depends(verify_token)):
    if request.permission is not None and depends.get("uid") == user_id:
        return ErrorResponse(msg="无法修改自己的权限")
    update_result = USER_CLIENT.update_user(user_id=user_id, password=request.password, permission=request.permission)
    return SuccessResponse(data={
        "update_result": update_result
    })


@AUTH_ROUTER.patch("/edit_self")
def edit_self(request: EditUserRequest, payload: dict = Depends(verify_token)):
    user_id = payload.get("uid",0)
    if request.permission is not None:
        return ErrorResponse(msg="只允许修改密码")
    update_result = USER_CLIENT.update_user(user_id=user_id, password=request.password, permission=request.permission)
    return SuccessResponse(data={
        "update_result": update_result
    })

@AUTH_ROUTER.get("/get_all_users")
@require_permission(1)
def get_all_users(payload: dict = Depends(verify_token)):
    return SuccessResponse(data=USER_CLIENT.get_all_users())

@TOTP_ROUTER.post("/list")
def list_totp(payload: dict = Depends(verify_token)):
    result =[]
    app_list = TOTP_CLIENT.get_all_apps(payload.get("uid", 0))
    for app in app_list:
        result.append({
            "messages": app.messages,
            "secret": None,
            "otp": TOTP_CLIENT.generate_totp(appId=app.appId) # type: ignore
        })
    return SuccessResponse(data=result)
        
class AddTotpAppRequest(BaseModel):
    otpauth_url: str

@TOTP_ROUTER.post("/add")
def add_totp_app(request: AddTotpAppRequest,payload: dict = Depends(verify_token)):
    app_info = utils.parse_otpauth_url(request.otpauth_url,payload.get("uid",0))
    insert_result = TOTP_CLIENT.add_totp_app(app_info)
    return SuccessResponse(data={
        "app_id": insert_result
    })


@app.get("/api/config")
def status():
    return SuccessResponse(data={
        "enable_registration": config_manager.get("auth.enable_registration", False),
        "total_users": len(USER_CLIENT.get_all_users())
    })


    
    
    

    




