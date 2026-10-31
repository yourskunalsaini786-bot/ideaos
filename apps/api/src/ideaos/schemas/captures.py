"""Capture and Asset schemas."""
from uuid import UUID
from typing import Optional, List, Dict, Any, Literal
from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime


class CaptureBase(BaseModel):
    """Base capture schema."""
    type: Literal["voice", "image", "file", "link", "text"]
    source_text: Optional[str] = None
    metadata: Dict[str, Any] = {}
    idempotency_key: Optional[str] = None


class CaptureCreate(CaptureBase):
    """Schema for creating a capture."""
    pass


class CaptureUpdate(BaseModel):
    """Schema for updating a capture."""
    source_text: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    status: Optional[Literal["uploading", "processing", "completed", "failed"]] = None
    error_message: Optional[str] = None


class PresignedUploadResponse(BaseModel):
    """Response with presigned upload URL."""
    capture_id: UUID
    status: str
    presigned_upload: Dict[str, Any]
    created_at: datetime


class AssetCompleteRequest(BaseModel):
    """Request to complete asset upload."""
    capture_id: UUID
    checksum: str
    metadata: Dict[str, Any] = {}


class AssetCompleteResponse(BaseModel):
    """Response after asset upload completion."""
    asset_id: UUID
    capture_id: UUID
    status: str
    message: str


class AssetPresignRequest(BaseModel):
    """Request for presigned download URL."""
    asset_id: UUID
    operation: Literal["download", "view"] = "download"
    ttl_seconds: int = 3600


class AssetPresignResponse(BaseModel):
    """Response with presigned download URL."""
    url: str
    expires_at: datetime


class CaptureResponse(BaseModel):
    """Schema for capture response."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    workspace_id: UUID
    user_id: UUID
    type: str
    status: str
    source_text: Optional[str] = None
    metadata: Dict[str, Any]
    asset_id: Optional[UUID] = None
    idea_id: Optional[UUID] = None
    error_message: Optional[str] = None
    processing_started_at: Optional[datetime] = None
    processing_completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class AssetResponse(BaseModel):
    """Schema for asset response."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    workspace_id: UUID
    capture_id: Optional[UUID] = None
    storage_key: str
    bucket: str
    mime_type: str
    size_bytes: int
    checksum: str
    original_filename: Optional[str] = None
    status: str
    scan_result: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime


class CaptureListResponse(BaseModel):
    """Paginated capture list response."""
    data: List[CaptureResponse]
    next_cursor: Optional[str] = None
    has_more: bool