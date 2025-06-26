from database_clients.base import BaseDatabaseClient
from typing import Dict, Any, List, Optional
from hashlib import sha256
import hmac
import time
from dataclasses import dataclass
import os

@dataclass
class UserInfo:
    user_id: int | str
    username: str
    password_hash: str
    permission: int

class UserManager:
    def __init__(self,db: BaseDatabaseClient):
        self.db = db
    def _hash_password(self, password: str):
        salt = os.urandom(16)
        hash_digest = sha256(password.encode('utf-8')).hexdigest()
        return f"{salt.hex()}:{hash_digest}"
        
    def verify_password(self,username: str,password: str,salt: str):
        hash_digest = sha256(password.encode('utf-8')).hexdigest()
        except_user_pass_hash = self.db.query(["username",username])[0].get('password_hash')
        user_pass_hash = f"{salt}:{hash_digest}"
        if user_pass_hash == except_user_pass_hash:
            return True
        return False
        
    def add_user(self,username: str,password: str):
        permission = 0
        if len(self.db.query_all()) == 0:
            permission = 1
        if len(self.db.query(["username",username])) > 0:
            raise ValueError(f"User {username} already exists.")
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters long.")
        password_hash = self._hash_password(password)
        insert_result = self.db.insert({
                "username": username,
                "password_hash": password_hash,
                "permission": permission
        })
        return insert_result
        
    def del_user(self, username: str):
        user = self.db.query(["username", username])
        if not user:
            raise ValueError(f"User {username} does not exist.")
        delete_result = self.db.delete(["username", username])
        return delete_result
        
    def get_user(self,username: str):
        user = self.db.query(["username", username])
        if not user:
            raise ValueError(f"User {username} does not exist.")
        return UserInfo(
                user_id=user[0].doc_id,
                username=user[0]['username'],
                password_hash=user[0]['password_hash'],
                permission=user[0]['permission']
            )
    
    def update_user(self,user_id: str | int,password: Optional[str] = None, permission: Optional[int] = None):
        user = self.db.get_by_id(user_id)
        if not user:
            raise ValueError(f"User with ID {user_id} does not exist.")
        username = user['username']
        update_data: Dict[str, Any] = {}
        if password is not None:
            update_data['password_hash'] = self._hash_password(password)
        if permission is not None:
            update_data['permission'] = permission
        
        if len(update_data) == 0:
            raise ValueError("No fields to update.")
        
        update_result = self.db.update(["username",username], update_data)
        return update_result
    
    def get_all_users(self):
        return self.db.query_all()

        

