import pyotp
from database_clients.base import BaseDatabaseClient
from typing import List

class TOTPConfig:
    def __init__(self,appId: int | str,messages: List[str], secret: str,user_id: int,digit: int = 6):
        self.appId = appId
        self.messages = messages
        self.secret = secret
        self.user_id = user_id
        self.digit = digit

class NewTOTPConfig:
    def __init__(self,messages: List[str], secret: str,user_id: int | str,digit: int = 6):
        self.messages = messages
        self.secret = secret
        self.user_id = user_id
        self.digit = digit



class TOTPClient:
    def __init__(self,db: BaseDatabaseClient):
        self.db = db
    
    def add_totp_app(self,cfg: NewTOTPConfig):
        if len(cfg.messages) == 0:
            raise ValueError("Messages cannot be empty.")
        insert_result = self.db.insert({
            "issuer": cfg.messages[0],
            "account": cfg.messages[1],
            "secret": cfg.secret,
            "digit": cfg.digit,
            "user": cfg.user_id
        })
        if not insert_result:
            raise RuntimeError("Failed to insert TOTP configuration into the database.")
        return insert_result
    
    def generate_totp(self, appId: int):
        app_cfg = self.db.get_by_id(appId)
        if not app_cfg:
            raise ValueError(f"No TOTP configuration found for appId {appId}.")
        app_cfg = app_cfg
        totp = pyotp.TOTP(app_cfg['secret'], digits=app_cfg['digit'])
        return totp.now()
    
    def get_all_apps(self,user_id: int | str):
        apps = self.db.query(["user",user_id])
        if not apps:
            return []
        return [TOTPConfig(
            appId=app.doc_id,
            messages=[app['issuer'], app['account']],
            secret=app['secret'],
            user_id=app['user'],
            digit=app['digit']
        ) for app in apps]
    

