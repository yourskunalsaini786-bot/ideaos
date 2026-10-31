"""Workspace schemas."""
from uuid import UUID
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from datetime import datetime


class WorkspaceBase(BaseModel):
    """Base workspace schema."""
    name: str = Field(..., min_length=1, max_length=255)
    slug: str = Field(..., min_length=1, max_length=100, pattern=r"^[a-z0-9-]+$")
    settings: Dict[str, Any] = {}


class WorkspaceCreate(WorkspaceBase):
    """Schema for creating a workspace."""
    pass


class WorkspaceUpdate(BaseModel):
    """Schema for updating a workspace."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    settings: Optional[Dict[str, Any]] = None
    subscription_tier: Optional[str] = None
    subscription_status: Optional[str] = None


class WorkspaceResponse(WorkspaceBase):
    """Schema for workspace response."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    owner_id: UUID
    subscription_tier: str
    subscription_status: str
    created_at: datetime
    updated_at: datetime


class WorkspaceMemberBase(BaseModel):
    """Base workspace member schema."""
    role: str = Field(..., pattern=r"^(owner|admin|editor|member|viewer|contributor)$")


class WorkspaceInviteRequest(WorkspaceMemberBase):
    """Schema for inviting a member."""
    email: EmailStr
    invited_by: Optional[UUID] = None


class WorkspaceMemberResponse(BaseModel):
    """Schema for workspace member response."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    workspace_id: UUID
    user_id: UUID
    role: str
    invited_by: Optional[UUID] = None
    joined_at: datetime
    user: Optional["UserBasic"] = None


class UserBasic(BaseModel):
    """Basic user info for nested responses."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: str
    name: Optional[str] = None
    avatar_url: Optional[str] = None


# Resolve forward references
WorkspaceMemberResponse.model_rebuild()