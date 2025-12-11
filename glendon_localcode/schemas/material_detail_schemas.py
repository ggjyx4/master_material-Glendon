from datetime import datetime
from typing import Optional, List, Any, Dict
from pydantic import BaseModel, Field

# --- Shared Request Model ---
class MaterialIDRequest(BaseModel):
    document_id: str = Field(..., description="The unique document ID")

# --- Response Models ---
class MaterialDetailResponse(BaseModel):
    # Meta
    document_id: str
    document_uid: Optional[str] = None
    ver_num: int
    status: Optional[str] = None
    
    # Header Info
    master_material_id: Optional[str] = None
    material_name: Optional[str] = None
    ref_id: Optional[str] = None
    material_type: Optional[str] = None
    supplier_name: Optional[str] = None
    country_of_origin: Optional[str] = None
    
    # Media / Links
    qr_id: Optional[str] = None
    hanger_pdf_id: Optional[str] = None
    picture_id: Optional[str] = None
    
    # Audit
    created_by: Optional[str] = None
    created_at: Optional[Any] = None
    submitted_at: Optional[Any] = None
    last_verified_date: Optional[Any] = None
    
    # Cost Summary for Header
    cost_display: Optional[str] = None 
    verification_status: Optional[str] = None

class TechnicalDetailResponse(BaseModel):
    # Spec Fields
    unit_of_measurement: Optional[str] = None
    fabric_composition: Optional[Any] = None  # JSON
    generic_material_composition: Optional[str] = None
    
    fabric_roll_width: Optional[float] = None
    fabric_cut_width: Optional[float] = None
    fabric_cut_width_no_shrinkage: Optional[float] = None
    
    weight_per_unit: Optional[float] = None
    weight_uom: Optional[str] = None
    generic_material_size: Optional[str] = None
    
    weft_shrinkage: Optional[float] = None
    werp_shrinkage: Optional[float] = None
    
    estimated_logistics_lead_time: Optional[int] = None

class CostDetailResponse(BaseModel):
    original_cost_per_unit: Optional[float] = None
    native_cost_currency: Optional[str] = None
    
    supplier_selling_tolerance: Optional[float] = None
    refundable_tolerance: Optional[bool] = None
    effective_cost_per_unit: Optional[float] = None
    
    vietnam_vat_rate: Optional[str] = None
    refundable_vat: Optional[bool] = None
    
    import_duty: Optional[float] = None
    refundable_import_duty: Optional[bool] = None
    
    shipping_term: Optional[str] = None
    logistics_rate: Optional[float] = None
    logistics_fee_per_unit: Optional[float] = None
    
    landed_cost_per_unit: Optional[float] = None

class VersionHistoryItem(BaseModel):
    ver_num: int
    submitted_by: Optional[str] = ""
    submitted_at: Optional[Any] = None
    change_description: Optional[str] = ""