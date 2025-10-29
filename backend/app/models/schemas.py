from pydantic import BaseModel, Field, EmailStr
from typing import Optional, Dict
from datetime import datetime


class ProjectBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    domain: str = Field(..., min_length=1, max_length=255)
    compose_content: str = Field(..., min_length=1)
    env_vars: Optional[Dict[str, str]] = Field(default_factory=dict)


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    domain: Optional[str] = Field(None, min_length=1, max_length=255)
    compose_content: Optional[str] = Field(None, min_length=1)
    env_vars: Optional[Dict[str, str]] = None


class ProjectResponse(ProjectBase):
    id: int
    slug: str
    owner_id: int
    status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ProjectListResponse(BaseModel):
    projects: list[ProjectResponse]
    total: int


# ========== User Schemas ==========

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=255)
    email: Optional[EmailStr] = None
    system_user: str = Field(default="docklite", min_length=1, max_length=255)
    
    @classmethod
    def model_validate(cls, obj):
        # Convert empty string to None for email
        if isinstance(obj, dict) and obj.get('email') == '':
            obj['email'] = None
        return super().model_validate(obj)


class UserCreate(UserBase):
    password: str = Field(..., min_length=6)


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(UserBase):
    id: int
    is_active: bool
    is_admin: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    username: Optional[str] = None

