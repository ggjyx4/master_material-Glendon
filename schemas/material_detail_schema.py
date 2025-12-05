import anvil.server
from datetime import datetime
from typing import Optional, List, Any, Dict
from pydantic import BaseModel, Field


# --- Shared Request Model ---
class MaterialIDRequest(BaseModel):
    document_id: str = Field(None, description="The unique document ID of the material")

# --- Response Models ---
class MaterialDetailResponse(BaseModel):
    document_id: str
    ver_num: str
    master_material_id: str
    name: str
    ref_id: str
    material_type: str
    supplier: str
    country_of_origin: str
    created_by: str
    created_at: Optional[datetime]
    fabric_composition: str
    weight_per_unit: Optional[int]
    fabric_roll_width: Optional[int]
    fabric_cut_width: Optional[int]
    original_cost_per_unit: Optional[int]
    cost_display: str
    unit_of_measurement: str
    verification_status: str
    updated_at: Optional[Any] = None
    submitted_at: Optional[Any] = None
    last_verified_date: Optional[Any] = None

class TechnicalDetailResponse(BaseModel):
    fabric_composition: Optional[str] = None
    fabric_roll_width: Optional[float] = None
    fabric_cut_width: Optional[float] = None
    fabric_cut_width_no_shrinkage: Optional[float] = None
    weight_per_unit: Optional[float] = None
    weft_shrinkage: Optional[float] = None
    werp_shrinkage: Optional[float] = None

class CostDetailResponse(BaseModel):
    original_cost_per_unit: Optional[float] = None
    currency: Optional[str] = None
    supplier_tolerance: Optional[float] = None
    effective_cost: Optional[float] = None
    vat: Optional[float] = None
    import_duty: Optional[float] = None
    logistics_rate: Optional[float] = None
    landed_cost: Optional[float] = None

class VersionHistoryItem(BaseModel):
    ver_num: int
    submitted_by: str
    submitted_at: Optional[Any] = None
    change_description: str

