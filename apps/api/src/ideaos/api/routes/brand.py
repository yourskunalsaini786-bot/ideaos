"""Brand routes."""
from uuid import UUID
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from ideaos.core.database import get_db
from ideaos.models import BrandProfile, BrandRule
from ideaos.schemas.brand import (
    BrandProfileCreate,
    BrandProfileUpdate,
    BrandProfileResponse,
    BrandRuleCreate,
    BrandRuleUpdate,
    BrandRuleResponse,
    BrandRuleListResponse,
    BrandValidationRequest,
    BrandValidationResult,
    BrandExtractRulesRequest,
    BrandExtractRulesResponse,
)

router = APIRouter()


async def get_current_workspace_id(request: Request) -> UUID:
    """Extract workspace_id from request state."""
    workspace_id = getattr(request.state, "workspace_id", None)
    if not workspace_id:
        raise HTTPException(status_code=401, detail="Workspace context required")
    return UUID(workspace_id)


async def get_current_user_id(request: Request) -> UUID:
    """Extract user_id from request state."""
    user_id = getattr(request.state, "user_id", None)
    if not user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    return UUID(user_id)


# Brand Profile routes
@router.get("/profile", response_model=BrandProfileResponse)
async def get_brand_profile(
    request: Request,
    db: AsyncSession = Depends(get_db),
    workspace_id: UUID = Depends(get_current_workspace_id),
):
    """Get brand profile for current workspace."""
    result = await db.execute(
        select(BrandProfile)
        .where(BrandProfile.workspace_id == workspace_id)
        .options(selectinload(BrandProfile.rules))
    )
    profile = result.scalar_one_or_none()
    if not profile:
        # Create default profile if not exists
        profile = BrandProfile(workspace_id=workspace_id)
        db.add(profile)
        await db.commit()
        await db.refresh(profile)
    return profile


@router.post("/profile", response_model=BrandProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_brand_profile(
    profile_in: BrandProfileCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    workspace_id: UUID = Depends(get_current_workspace_id),
):
    """Create brand profile for workspace."""
    # Check if profile already exists
    result = await db.execute(
        select(BrandProfile).where(BrandProfile.workspace_id == workspace_id)
    )
    existing = result.scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="Brand profile already exists for this workspace")

    profile = BrandProfile(
        workspace_id=workspace_id,
        **profile_in.model_dump(),
    )
    db.add(profile)
    await db.commit()
    await db.refresh(profile)
    return profile


@router.patch("/profile", response_model=BrandProfileResponse)
async def update_brand_profile(
    profile_in: BrandProfileUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    workspace_id: UUID = Depends(get_current_workspace_id),
    user_id: UUID = Depends(get_current_user_id),
):
    """Update brand profile."""
    result = await db.execute(
        select(BrandProfile).where(BrandProfile.workspace_id == workspace_id)
    )
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Brand profile not found")

    update_data = profile_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(profile, field, value)

    profile.version += 1
    await db.commit()
    await db.refresh(profile)
    return profile


# Brand Rules routes
@router.get("/rules", response_model=BrandRuleListResponse)
async def list_brand_rules(
    request: Request,
    db: AsyncSession = Depends(get_db),
    workspace_id: UUID = Depends(get_current_workspace_id),
    rule_type: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    cursor: Optional[str] = Query(None),
    limit: int = Query(50, le=200),
):
    """List brand rules for workspace."""
    query = select(BrandRule).where(BrandRule.workspace_id == workspace_id)

    if rule_type:
        query = query.where(BrandRule.rule_type == rule_type)
    if is_active is not None:
        query = query.where(BrandRule.is_active == is_active)
    if cursor:
        from datetime import datetime
        try:
            cursor_dt = datetime.fromisoformat(cursor.replace("Z", "+00:00"))
            query = query.where(BrandRule.created_at < cursor_dt)
        except ValueError:
            pass

    query = query.order_by(BrandRule.created_at.desc()).limit(limit + 1)
    result = await db.execute(query)
    rules = result.scalars().all()

    has_more = len(rules) > limit
    if has_more:
        rules = rules[:limit]

    next_cursor = None
    if has_more and rules:
        next_cursor = rules[-1].created_at.isoformat()

    return BrandRuleListResponse(data=rules, next_cursor=next_cursor, has_more=has_more)


@router.post("/rules", response_model=BrandRuleResponse, status_code=status.HTTP_201_CREATED)
async def create_brand_rule(
    rule_in: BrandRuleCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    workspace_id: UUID = Depends(get_current_workspace_id),
    user_id: UUID = Depends(get_current_user_id),
):
    """Create a brand rule."""
    # Get or create brand profile
    result = await db.execute(
        select(BrandProfile).where(BrandProfile.workspace_id == workspace_id)
    )
    profile = result.scalar_one_or_none()
    if not profile:
        profile = BrandProfile(workspace_id=workspace_id)
        db.add(profile)
        await db.flush()

    rule = BrandRule(
        workspace_id=workspace_id,
        brand_profile_id=profile.id,
        created_by=user_id,
        **rule_in.model_dump(),
    )
    db.add(rule)
    await db.commit()
    await db.refresh(rule)
    return rule


@router.get("/rules/{rule_id}", response_model=BrandRuleResponse)
async def get_brand_rule(
    rule_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
    workspace_id: UUID = Depends(get_current_workspace_id),
):
    """Get brand rule by ID."""
    result = await db.execute(
        select(BrandRule).where(BrandRule.id == rule_id, BrandRule.workspace_id == workspace_id)
    )
    rule = result.scalar_one_or_none()
    if not rule:
        raise HTTPException(status_code=404, detail="Brand rule not found")
    return rule


@router.patch("/rules/{rule_id}", response_model=BrandRuleResponse)
async def update_brand_rule(
    rule_id: UUID,
    rule_in: BrandRuleUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    workspace_id: UUID = Depends(get_current_workspace_id),
):
    """Update brand rule."""
    result = await db.execute(
        select(BrandRule).where(BrandRule.id == rule_id, BrandRule.workspace_id == workspace_id)
    )
    rule = result.scalar_one_or_none()
    if not rule:
        raise HTTPException(status_code=404, detail="Brand rule not found")

    update_data = rule_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(rule, field, value)

    await db.commit()
    await db.refresh(rule)
    return rule


@router.delete("/rules/{rule_id}")
async def delete_brand_rule(
    rule_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
    workspace_id: UUID = Depends(get_current_workspace_id),
):
    """Delete brand rule."""
    result = await db.execute(
        select(BrandRule).where(BrandRule.id == rule_id, BrandRule.workspace_id == workspace_id)
    )
    rule = result.scalar_one_or_none()
    if not rule:
        raise HTTPException(status_code=404, detail="Brand rule not found")

    await db.delete(rule)
    await db.commit()
    return {"message": "Brand rule deleted"}


# Brand validation and extraction
@router.post("/validate", response_model=BrandValidationResult)
async def validate_content(
    request_in: BrandValidationRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    workspace_id: UUID = Depends(get_current_workspace_id),
):
    """Validate content against brand rules."""
    # Get active brand rules for workspace
    result = await db.execute(
        select(BrandRule)
        .where(
            BrandRule.workspace_id == workspace_id,
            BrandRule.is_active == True,
        )
    )
    rules = result.scalars().all()

    violations = []
    warnings = []
    suggestions = []
    score = 10.0

    content = request_in.content.lower()

    for rule in rules:
        # Filter by platform applicability
        if rule.applies_to and request_in.platform and "all" not in rule.applies_to:
            if request_in.platform not in rule.applies_to:
                continue

        # Check pattern if provided
        if rule.pattern:
            import re
            if re.search(rule.pattern, content):
                if rule.severity == "error":
                    violations.append({
                        "rule_id": str(rule.id),
                        "rule_type": rule.rule_type,
                        "message": rule.message,
                        "pattern": rule.pattern,
                    })
                    score -= 2.0
                elif rule.severity == "warning":
                    warnings.append({
                        "rule_id": str(rule.id),
                        "rule_type": rule.rule_type,
                        "message": rule.message,
                        "pattern": rule.pattern,
                    })
                    score -= 1.0

    score = max(0.0, score)
    passed = len(violations) == 0

    # Add suggestions based on brand profile
    profile_result = await db.execute(
        select(BrandProfile).where(BrandProfile.workspace_id == workspace_id)
    )
    profile = profile_result.scalar_one_or_none()
    if profile:
        if profile.vocabulary_preferences:
            preferred = profile.vocabulary_preferences.get("preferred", [])
            for word in preferred:
                if word.lower() not in content:
                    suggestions.append(f"Consider using '{word}'")

    return BrandValidationResult(
        passed=passed,
        score=round(score, 1),
        violations=violations,
        warnings=warnings,
        suggestions=suggestions,
    )


@router.post("/extract-rules", response_model=BrandExtractRulesResponse)
async def extract_rules_from_edit(
    request_in: BrandExtractRulesRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    workspace_id: UUID = Depends(get_current_workspace_id),
):
    """Extract brand rules from edit diff (placeholder for ML-based extraction)."""
    # TODO: Implement actual ML-based rule extraction
    # This would analyze the diff between original and edited content
    # and propose new brand rules

    proposed_rules = []
    summary = "Analysis complete. No automatic rules extracted."

    # Simple heuristic: check for removed words (might be prohibited phrases)
    import re
    original_words = set(re.findall(r'\b\w+\b', request_in.original_content.lower()))
    edited_words = set(re.findall(r'\b\w+\b', request_in.edited_content.lower()))

    removed_words = original_words - edited_words
    added_words = edited_words - original_words

    if removed_words:
        for word in list(removed_words)[:5]:  # Limit to 5
            if len(word) > 3:  # Skip short words
                proposed_rules.append(BrandRuleCreate(
                    rule_type="must_avoid",
                    pattern=word,
                    severity="warning",
                    message=f"Avoid using '{word}' based on edit history",
                    examples=[f"Removed '{word}' from {request_in.platform} {request_in.format}"],
                    applies_to=[request_in.platform],
                ))

    if added_words:
        for word in list(added_words)[:5]:
            if len(word) > 3:
                proposed_rules.append(BrandRuleCreate(
                    rule_type="must_include",
                    pattern=word,
                    severity="info",
                    message=f"Consider including '{word}' based on edit history",
                    examples=[f"Added '{word}' to {request_in.platform} {request_in.format}"],
                    applies_to=[request_in.platform],
                ))

    if proposed_rules:
        summary = f"Extracted {len(proposed_rules)} proposed rules from edit diff"

    return BrandExtractRulesResponse(
        proposed_rules=proposed_rules,
        summary=summary,
    )