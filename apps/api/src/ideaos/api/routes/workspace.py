"""Workspace routes."""
from uuid import UUID
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from ideaos.core.database import get_db
from ideaos.core.security import TokenData, decode_token
from ideaos.models import Workspace, WorkspaceMember, User
from ideaos.schemas.workspace import (
    WorkspaceCreate,
    WorkspaceUpdate,
    WorkspaceResponse,
    WorkspaceMemberResponse,
    WorkspaceInviteRequest,
)

from ideaos.core.config import get_settings

settings = get_settings()
router = APIRouter()


async def get_current_workspace_id(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> UUID:
    """Extract workspace_id from request state (set by middleware) or dev fallback."""
    workspace_id = getattr(request.state, "workspace_id", None)
    if workspace_id:
        return UUID(str(workspace_id))
    if settings.ENVIRONMENT == "development":
        result = await db.execute(select(Workspace.id).limit(1))
        ws_id = result.scalar_one_or_none()
        if ws_id:
            return ws_id
        return UUID("00000000-0000-0000-0000-000000000001")
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Workspace context required",
    )


async def get_current_user_id(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> UUID:
    """Extract user_id from request state or dev fallback."""
    user_id = getattr(request.state, "user_id", None)
    if user_id:
        return UUID(str(user_id))
    if settings.ENVIRONMENT == "development":
        result = await db.execute(select(User.id).limit(1))
        u_id = result.scalar_one_or_none()
        if u_id:
            return u_id
        return UUID("00000000-0000-0000-0000-000000000002")
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication required",
    )


async def get_current_user_role(request: Request) -> str:
    """Extract user role from request state."""
    return getattr(request.state, "user_role", "viewer")


@router.get("", response_model=List[WorkspaceResponse])
async def list_workspaces(
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
):
    """List workspaces for current user."""
    result = await db.execute(
        select(Workspace)
        .join(WorkspaceMember, Workspace.id == WorkspaceMember.workspace_id)
        .where(WorkspaceMember.user_id == user_id)
        .options(selectinload(Workspace.owner))
    )
    workspaces = result.scalars().all()
    return workspaces


@router.post("", response_model=WorkspaceResponse, status_code=status.HTTP_201_CREATED)
async def create_workspace(
    workspace_in: WorkspaceCreate,
    db: AsyncSession = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
):
    """Create a new workspace."""
    workspace = Workspace(
        name=workspace_in.name,
        slug=workspace_in.slug,
        owner_id=user_id,
        settings=workspace_in.settings or {},
    )
    db.add(workspace)
    await db.flush()

    # Add owner as member
    member = WorkspaceMember(
        workspace_id=workspace.id,
        user_id=user_id,
        role="owner",
    )
    db.add(member)

    await db.commit()
    await db.refresh(workspace)
    return workspace


@router.get("/{workspace_id}", response_model=WorkspaceResponse)
async def get_workspace(
    workspace_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_workspace_id: UUID = Depends(get_current_workspace_id),
):
    """Get workspace by ID."""
    if workspace_id != current_workspace_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )

    result = await db.execute(
        select(Workspace)
        .where(Workspace.id == workspace_id)
        .options(selectinload(Workspace.owner))
    )
    workspace = result.scalar_one_or_none()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    return workspace


@router.patch("/{workspace_id}", response_model=WorkspaceResponse)
async def update_workspace(
    workspace_id: UUID,
    workspace_in: WorkspaceUpdate,
    db: AsyncSession = Depends(get_db),
    current_workspace_id: UUID = Depends(get_current_workspace_id),
    user_role: str = Depends(get_current_user_role),
):
    """Update workspace settings."""
    if workspace_id != current_workspace_id:
        raise HTTPException(status_code=403, detail="Access denied")

    if user_role not in ["owner", "admin"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    result = await db.execute(select(Workspace).where(Workspace.id == workspace_id))
    workspace = result.scalar_one_or_none()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    update_data = workspace_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(workspace, field, value)

    await db.commit()
    await db.refresh(workspace)
    return workspace


@router.get("/{workspace_id}/members", response_model=List[WorkspaceMemberResponse])
async def list_workspace_members(
    workspace_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_workspace_id: UUID = Depends(get_current_workspace_id),
):
    """List workspace members."""
    if workspace_id != current_workspace_id:
        raise HTTPException(status_code=403, detail="Access denied")

    result = await db.execute(
        select(WorkspaceMember)
        .where(WorkspaceMember.workspace_id == workspace_id)
        .options(selectinload(WorkspaceMember.user))
    )
    members = result.scalars().all()
    return members


@router.post("/{workspace_id}/invite", response_model=WorkspaceMemberResponse)
async def invite_member(
    workspace_id: UUID,
    invite: WorkspaceInviteRequest,
    db: AsyncSession = Depends(get_db),
    current_workspace_id: UUID = Depends(get_current_workspace_id),
    user_role: str = Depends(get_current_user_role),
):
    """Invite a user to workspace."""
    if workspace_id != current_workspace_id:
        raise HTTPException(status_code=403, detail="Access denied")

    if user_role not in ["owner", "admin"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    # Check if user exists
    result = await db.execute(select(User).where(User.email == invite.email))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check if already a member
    result = await db.execute(
        select(WorkspaceMember)
        .where(
            WorkspaceMember.workspace_id == workspace_id,
            WorkspaceMember.user_id == user.id,
        )
    )
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="User already a member")

    member = WorkspaceMember(
        workspace_id=workspace_id,
        user_id=user.id,
        role=invite.role,
        invited_by=invite.invited_by,
    )
    db.add(member)
    await db.commit()
    await db.refresh(member)
    return member


@router.delete("/{workspace_id}/members/{user_id}")
async def remove_member(
    workspace_id: UUID,
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_workspace_id: UUID = Depends(get_current_workspace_id),
    user_role: str = Depends(get_current_user_role),
    current_user_id: UUID = Depends(get_current_user_id),
):
    """Remove a member from workspace."""
    if workspace_id != current_workspace_id:
        raise HTTPException(status_code=403, detail="Access denied")

    if user_role not in ["owner", "admin"] and user_id != current_user_id:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    result = await db.execute(
        select(WorkspaceMember)
        .where(
            WorkspaceMember.workspace_id == workspace_id,
            WorkspaceMember.user_id == user_id,
        )
    )
    member = result.scalar_one_or_none()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")

    # Prevent removing owner
    if member.role == "owner":
        raise HTTPException(status_code=400, detail="Cannot remove workspace owner")

    await db.delete(member)
    await db.commit()
    return {"message": "Member removed"}