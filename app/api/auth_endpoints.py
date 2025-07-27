from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from typing import Optional
import hashlib
import secrets

auth_router = APIRouter()

# Mock user database (in real app, this would be PostgreSQL)
fake_users_db = {}
fake_sessions = {}

class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: Optional[str] = None

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: Optional[str]
    is_active: bool

@auth_router.post("/register", response_model=UserResponse)
def register_user(user: UserRegister):
    """Register a new user"""
    if user.username in fake_users_db:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    # Hash password (simple version)
    hashed_password = hashlib.sha256(user.password.encode()).hexdigest()
    
    user_data = {
        "id": len(fake_users_db) + 1,
        "username": user.username,
        "email": user.email,
        "full_name": user.full_name,
        "password": hashed_password,
        "is_active": True
    }
    
    fake_users_db[user.username] = user_data
    
    return UserResponse(**{k: v for k, v in user_data.items() if k != "password"})

@auth_router.post("/login")
def login_user(user: UserLogin):
    """Login user and get access token"""
    if user.username not in fake_users_db:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    stored_user = fake_users_db[user.username]
    hashed_password = hashlib.sha256(user.password.encode()).hexdigest()
    
    if stored_user["password"] != hashed_password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Create session token
    token = secrets.token_urlsafe(32)
    fake_sessions[token] = user.username
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": UserResponse(**{k: v for k, v in stored_user.items() if k != "password"})
    }

@auth_router.get("/me", response_model=UserResponse)
def get_current_user(token: str):
    """Get current user info"""
    if token not in fake_sessions:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    username = fake_sessions[token]
    user_data = fake_users_db[username]
    
    return UserResponse(**{k: v for k, v in user_data.items() if k != "password"})