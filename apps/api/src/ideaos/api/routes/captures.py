"""Capture routes."""
from uuid import UUID
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
import boto3
from botocore.config import Config as BotoConfig
import hashlib

from ideaos.core.config import get_settings
from ideaos.core.database import get_db
from ideaos.models import Capture, Asset
from ideaos.schemas.captures import (
    CaptureCreate,
    CaptureUpdate,
    CaptureResponse,
    CaptureListResponse,
    PresignedUploadResponse,
    AssetCompleteRequest,
    AssetCompleteResponse,
    AssetPresignRequest,
    AssetPresignResponse,
    AssetResponse,
)

router = APIRouter()
settings = get_settings()


def get_r2_client():
    """Get Cloudflare R2 S3 client."""
    return boto3.client(
        "s3",
        endpoint_url=f"https://{settings.R2_ACCOUNT_ID}.r2.cloudflarestorage.com",
        aws_access_key_id=settings.R2_ACCESS_KEY_ID,
        aws_secret_access_key=settings.R2_SECRET_ACCESS_KEY,
        config=BotoConfig(signature_version="s3v4"),
        region_name="auto",
    )


async def get_current_workspace_id(request: Request, db: AsyncSession = Depends(get_db)) -> UUID:
    """Extract workspace_id from request state with dev fallback."""
    workspace_id = getattr(request.state, "workspace_id", None)
    if workspace_id:
        return UUID(str(workspace_id))
    if settings.ENVIRONMENT == "development":
        from ideaos.models import Workspace
        result = await db.execute(select(Workspace.id).order_by(Workspace.created_at.asc()).limit(1))
        ws_id = result.scalar_one_or_none()
        if ws_id:
            return ws_id
        return UUID("00000000-0000-0000-0000-000000000001")
    raise HTTPException(status_code=401, detail="Workspace context required")


async def get_current_user_id(request: Request, db: AsyncSession = Depends(get_db)) -> UUID:
    """Extract user_id from request state with dev fallback."""
    user_id = getattr(request.state, "user_id", None)
    if user_id:
        return UUID(str(user_id))
    if settings.ENVIRONMENT == "development":
        from ideaos.models import User
        result = await db.execute(select(User.id).limit(1))
        u_id = result.scalar_one_or_none()
        if u_id:
            return u_id
        return UUID("00000000-0000-0000-0000-000000000002")
    raise HTTPException(status_code=401, detail="Authentication required")


@router.post("", response_model=PresignedUploadResponse, status_code=status.HTTP_201_CREATED)
async def create_capture(
    capture_in: CaptureCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    workspace_id: UUID = Depends(get_current_workspace_id),
    user_id: UUID = Depends(get_current_user_id),
):
    """Create a capture and return presigned upload URL for assets."""
    # Check idempotency
    if capture_in.idempotency_key:
        result = await db.execute(
            select(Capture).where(
                Capture.workspace_id == workspace_id,
                Capture.metadata.op("->>")("idempotency_key") == capture_in.idempotency_key,
            )
        )
        existing = result.scalar_one_or_none()
        if existing:
            return PresignedUploadResponse(
                capture_id=existing.id,
                status=existing.status,
                presigned_upload={},
                created_at=existing.created_at,
            )

    # Create capture record
    metadata = capture_in.metadata.copy()
    if capture_in.idempotency_key:
        metadata["idempotency_key"] = capture_in.idempotency_key

    capture = Capture(
        workspace_id=workspace_id,
        user_id=user_id,
        type=capture_in.type,
        status="uploading",
        source_text=capture_in.source_text,
        metadata=metadata,
    )
    db.add(capture)
    await db.flush()

    presigned_upload = {}
    asset = None

    # For file types, create asset record and presigned URL
    if capture_in.type in ["voice", "image", "file"] and capture_in.metadata.get("filename"):
        asset = Asset(
            workspace_id=workspace_id,
            capture_id=capture.id,
            storage_key=f"{workspace_id}/{capture.id}/{capture_in.metadata['filename']}",
            bucket=settings.R2_BUCKET,
            mime_type=capture_in.metadata.get("mime_type", "application/octet-stream"),
            size_bytes=capture_in.metadata.get("size_bytes", 0),
            checksum="",  # Will be verified on complete
            original_filename=capture_in.metadata.get("filename"),
            status="pending",
        )
        db.add(asset)
        await db.flush()

        capture.asset_id = asset.id

        # Generate presigned PUT URL
        r2_client = get_r2_client()
        presigned_url = r2_client.generate_presigned_url(
            "put_object",
            Params={
                "Bucket": settings.R2_BUCKET,
                "Key": asset.storage_key,
                "ContentType": asset.mime_type,
            },
            ExpiresIn=900,  # 15 minutes
        )
        presigned_upload = {
            "url": presigned_url,
            "method": "PUT",
            "headers": {"Content-Type": asset.mime_type},
            "expires_at": "15 minutes",
        }

    await db.commit()
    await db.refresh(capture)

    return PresignedUploadResponse(
        capture_id=capture.id,
        status=capture.status,
        presigned_upload=presigned_upload,
        created_at=capture.created_at,
    )


@router.post("/assets/complete", response_model=AssetCompleteResponse)
async def complete_asset_upload(
    request_in: AssetCompleteRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    workspace_id: UUID = Depends(get_current_workspace_id),
):
    """Complete asset upload - verify checksum and trigger processing."""
    result = await db.execute(
        select(Asset)
        .where(Asset.id == request_in.capture_id)  # Actually asset_id
    )
    asset = result.scalar_one_or_none()

    # Try to find by capture_id if not found by id
    if not asset:
        result = await db.execute(
            select(Asset).where(Asset.capture_id == request_in.capture_id)
        )
        asset = result.scalar_one_or_none()

    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    if asset.workspace_id != workspace_id:
        raise HTTPException(status_code=403, detail="Access denied")

    # Verify checksum by downloading from R2
    r2_client = get_r2_client()
    try:
        obj = r2_client.get_object(Bucket=settings.R2_BUCKET, Key=asset.storage_key)
        content = obj["Body"].read()
        calculated_checksum = hashlib.sha256(content).hexdigest()

        if calculated_checksum != request_in.checksum:
            asset.status = "failed"
            await db.commit()
            raise HTTPException(status_code=400, detail="Checksum mismatch")

        asset.checksum = calculated_checksum
        asset.metadata = {**asset.metadata, **request_in.metadata}
        asset.status = "scanned"

        # Update capture status
        if asset.capture_id:
            capture_result = await db.execute(
                select(Capture).where(Capture.id == asset.capture_id)
            )
            capture = capture_result.scalar_one_or_none()
            if capture:
                capture.status = "processing"
                capture.processing_started_at = func.now()

        await db.commit()

        return AssetCompleteResponse(
            asset_id=asset.id,
            capture_id=asset.capture_id or UUID(int=0),
            status="processing",
            message="Asset uploaded. Processing started.",
        )
    except Exception as e:
        asset.status = "failed"
        await db.commit()
        raise HTTPException(status_code=500, detail=f"Verification failed: {str(e)}")


@router.post("/assets/presign", response_model=AssetPresignResponse)
async def get_asset_presigned_url(
    request_in: AssetPresignRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    workspace_id: UUID = Depends(get_current_workspace_id),
):
    """Get presigned URL for downloading/viewing an asset."""
    result = await db.execute(
        select(Asset).where(Asset.id == request_in.asset_id)
    )
    asset = result.scalar_one_or_none()

    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    if asset.workspace_id != workspace_id:
        raise HTTPException(status_code=403, detail="Access denied")

    r2_client = get_r2_client()

    if request_in.operation == "download":
        presigned_url = r2_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": settings.R2_BUCKET, "Key": asset.storage_key},
            ExpiresIn=request_in.ttl_seconds,
        )
    else:
        presigned_url = r2_client.generate_presigned_url(
            "get_object",
            Params={
                "Bucket": settings.R2_BUCKET,
                "Key": asset.storage_key,
                "ResponseContentDisposition": "inline",
            },
            ExpiresIn=request_in.ttl_seconds,
        )

    from datetime import datetime, timedelta, timezone
    return AssetPresignResponse(
        url=presigned_url,
        expires_at=datetime.now(timezone.utc) + timedelta(seconds=request_in.ttl_seconds),
    )


@router.get("/{capture_id}", response_model=CaptureResponse)
async def get_capture(
    capture_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
    workspace_id: UUID = Depends(get_current_workspace_id),
):
    """Get capture by ID."""
    result = await db.execute(
        select(Capture)
        .where(Capture.id == capture_id, Capture.workspace_id == workspace_id)
        .options(selectinload(Capture.asset), selectinload(Capture.idea))
    )
    capture = result.scalar_one_or_none()
    if not capture:
        raise HTTPException(status_code=404, detail="Capture not found")
    return capture


@router.get("", response_model=CaptureListResponse)
async def list_captures(
    request: Request,
    db: AsyncSession = Depends(get_db),
    workspace_id: UUID = Depends(get_current_workspace_id),
    cursor: Optional[str] = Query(None),
    limit: int = Query(20, le=100),
    status: Optional[str] = Query(None),
    type: Optional[str] = Query(None),
):
    """List captures with pagination."""
    query = select(Capture).where(Capture.workspace_id == workspace_id)

    if status:
        query = query.where(Capture.status == status)
    if type:
        query = query.where(Capture.type == type)
    if cursor:
        # Simple cursor-based pagination using created_at
        try:
            cursor_dt = datetime.fromisoformat(cursor.replace("Z", "+00:00"))
            query = query.where(Capture.created_at < cursor_dt)
        except ValueError:
            pass

    query = query.order_by(Capture.created_at.desc()).limit(limit + 1)
    result = await db.execute(query)
    captures = result.scalars().all()

    has_more = len(captures) > limit
    if has_more:
        captures = captures[:limit]

    next_cursor = None
    if has_more and captures:
        next_cursor = captures[-1].created_at.isoformat()

    return CaptureListResponse(
        data=captures,
        next_cursor=next_cursor,
        has_more=has_more,
    )


@router.patch("/{capture_id}", response_model=CaptureResponse)
async def update_capture(
    capture_id: UUID,
    capture_in: CaptureUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    workspace_id: UUID = Depends(get_current_workspace_id),
):
    """Update capture metadata."""
    result = await db.execute(
        select(Capture).where(Capture.id == capture_id, Capture.workspace_id == workspace_id)
    )
    capture = result.scalar_one_or_none()
    if not capture:
        raise HTTPException(status_code=404, detail="Capture not found")

    update_data = capture_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(capture, field, value)

    await db.commit()
    await db.refresh(capture)
    return capture