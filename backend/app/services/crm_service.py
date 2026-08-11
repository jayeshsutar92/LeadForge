import json
from datetime import datetime, UTC
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.redis import build_redis_key, get_redis_client
from app.models.lead import Lead, Activity
from app.repositories.crm import CRMRepository
from app.schemas.crm import LeadCreate, LeadUpdate, ActivityCreate

_LEAD_CACHE_TTL = 1800  # 30 mins


class CRMService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repo = CRMRepository(session)
        self.redis = get_redis_client()

    def _cache_key(self, lead_id: str) -> str:
        return build_redis_key("lead", lead_id)

    async def _invalidate_cache(self, lead_id: UUID) -> None:
        await self.redis.delete(self._cache_key(str(lead_id)))

    # ─── Leads ────────────────────────────────────────────────────────────────

    async def get_lead(self, lead_id: UUID, user_id: UUID) -> Lead:
        key = self._cache_key(str(lead_id))
        cached = await self.redis.get(key)
        
        if cached:
            try:
                data = json.loads(cached)
                cached_id = data.get("id")
                if cached_id:
                    # Cache hit but we still need the DB object to return a `Lead` model instance
                    # that satisfies Pydantic from_attributes, or we can just fetch.
                    # We will just fetch to ensure relations (activities) are fresh.
                    pass
            except Exception:
                pass
                
        lead = await self.repo.get_lead(lead_id, user_id)
        if not lead:
            raise HTTPException(status_code=404, detail="Lead not found")
            
        payload = json.dumps({"id": str(lead.id)})
        await self.redis.set(key, payload, ex=_LEAD_CACHE_TTL)
        return lead

    async def get_lead_by_business(self, business_id: UUID, user_id: UUID) -> Lead | None:
        return await self.repo.get_lead_by_business(business_id, user_id)

    async def create_lead(self, payload: LeadCreate, current_user_id: UUID) -> Lead:
        # Check if lead already exists for this business
        existing = await self.repo.get_lead_by_business(payload.business_id, current_user_id)
        if existing:
            return existing

        lead = Lead(
            user_id=current_user_id,
            business_id=payload.business_id,
            status=payload.status,
            priority=payload.priority,
            source=payload.source,
            tags=payload.tags,
            next_follow_up=payload.next_follow_up,
            notes=payload.notes,
        )
        
        created = await self.repo.create_lead(lead)
        
        # Create an initial activity
        activity = Activity(
            lead_id=created.id,
            user_id=current_user_id,
            activity_type="system",
            description="Lead created",
        )
        await self.repo.create_activity(activity)
        
        # Need to reload to get activities populated
        return await self.get_lead(created.id, current_user_id)

    async def update_lead(self, lead_id: UUID, payload: LeadUpdate, current_user_id: UUID) -> Lead:
        lead = await self.get_lead(lead_id, current_user_id)
        
        update_data = {k: v for k, v in payload.model_dump().items() if v is not None}
        if not update_data:
            return lead
            
        old_status = lead.status
            
        updated = await self.repo.update_lead(lead_id, current_user_id, **update_data)
        
        # If status changed, log an activity automatically
        if "status" in update_data and update_data["status"] != old_status:
            activity = Activity(
                lead_id=lead_id,
                user_id=current_user_id,
                activity_type="stage_change",
                description=f"Stage changed from '{old_status}' to '{update_data['status']}'",
            )
            await self.repo.create_activity(activity)

        await self._invalidate_cache(lead_id)
        return await self.get_lead(lead_id, current_user_id)

    async def list_leads(
        self,
        user_id: UUID,
        q: str | None = None,
        status: str | None = None,
        assigned_to: UUID | None = None,
        min_priority: int | None = None,
        limit: int = 50,
        offset: int = 0,
        sort: str = "created_desc",
    ) -> tuple[int, list[Lead]]:
        return await self.repo.list_leads(
            user_id=user_id,
            q=q,
            status=status,
            assigned_to=assigned_to,
            min_priority=min_priority,
            limit=limit,
            offset=offset,
            sort=sort,
        )

    async def delete_lead(self, lead_id: UUID, user_id: UUID) -> None:
        deleted = await self.repo.delete_lead(lead_id, user_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Lead not found")
        await self._invalidate_cache(lead_id)

    # ─── Activities / Workflow ────────────────────────────────────────────────

    async def log_activity(self, lead_id: UUID, payload: ActivityCreate, current_user_id: UUID) -> Lead:
        lead = await self.get_lead(lead_id, current_user_id)
        
        activity = Activity(
            lead_id=lead_id,
            user_id=current_user_id,
            activity_type=payload.activity_type,
            description=payload.description,
            metadata_=payload.metadata_,
        )
        await self.repo.create_activity(activity)
        
        # Update last_contacted if it's a communication activity
        if payload.activity_type in ["call", "email", "meeting"]:
            await self.repo.update_lead(lead_id, current_user_id, last_contacted=datetime.now(UTC))
            
        await self._invalidate_cache(lead_id)
        return await self.get_lead(lead_id, current_user_id)
