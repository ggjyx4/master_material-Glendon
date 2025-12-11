from datetime import datetime
from typing import Optional, List, Any, Dict, Literal
from pydantic import BaseModel, Field, field_validator

class MaterialBase(BaseModel):
  """Common fields for creating/updating materials"""
  # --- Identification ---
  material_name: Optional[str] = None
  master_material_id: Optional[str] = None # Human readable ID
  ref_id: Optional[str] = None
  supplier_name: Optional[str] = None
  
  # --- Media & IDs (New) ---
  qr_id: Optional[str] = None
  hanger_pdf_id: Optional[str] = None
  picture_id: Optional[str] = None

  # --- Basic Specs ---
  material_type: Optional[str] = None
  country_of_origin: Optional[str] = None
  unit_of_measurement: Optional[str] = None
  
  # --- Technical Specs (Updated) ---
  fabric_composition: Optional[List[Any]] = None  # JSON structure: [[50, "Cotton"], [50, "Poly"]]
  generic_material_composition: Optional[str] = None # e.g. "Plastic" vs "Metal"
  
  fabric_roll_width: Optional[float] = None
  fabric_cut_width: Optional[float] = None
  fabric_cut_width_no_shrinkage: Optional[float] = None
  
  weight_per_unit: Optional[float] = None
  weight_uom: Optional[str] = None # e.g. "gsm" or "g/pc"
  
  generic_material_size: Optional[str] = None # e.g. "24L"
  
  weft_shrinkage: Optional[float] = None
  werp_shrinkage: Optional[float] = None

  # --- Logistics (New) ---
  estimated_logistics_lead_time: Optional[int] = None

  # --- Costs (Basic) ---
  original_cost_per_unit: Optional[float] = None
  native_cost_currency: Optional[str] = None
  supplier_selling_tolerance: Optional[float] = None
  refundable_tolerance: Optional[bool] = False
  effective_cost_per_unit: Optional[float] = None

  # --- Costs (Advanced / Taxes) ---
  vietnam_vat_rate: Optional[str] = None # "8%" or "10%"
  refundable_vat: Optional[bool] = False
  import_duty: Optional[float] = None
  refundable_import_duty: Optional[bool] = False
  shipping_term: Optional[str] = None # EXW, FOB, DDP
  logistics_rate: Optional[float] = None
  logistics_fee_per_unit: Optional[float] = None
  landed_cost_per_unit: Optional[float] = None

  # --- Notes ---
  change_description: Optional[str] = None

  @field_validator('*', mode='before')
  @classmethod
  def clean_data(cls, v):
    # If the DB or Form has an empty string, convert to None
    if isinstance(v, str) and not v.strip():
      return None
    return v

class CreateMaterialRequest(MaterialBase):
  """Request to create a new material"""
  pass

class UpdateDraftRequest(MaterialBase):
  """Request to update a draft"""
  document_id: str = Field(..., description="The ID of the master document")
  # We might update specific version fields, so we inherit MaterialBase

class SubmitVersionRequest(BaseModel):
  """Request to submit a version"""
  document_id: str = Field(..., description="The ID of the document to submit")
  form_data: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Final updates before submit")

class EditVerifiedRequest(BaseModel):
  """Request to edit a verified document (creates v+1)"""
  document_id: str = Field(..., description="The Verified Document ID")
  form_data: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Changes for the new version")
  notes: Optional[str] = Field(None, description="Notes for this revision")

class MaterialResponse(BaseModel):
  """Standard response for material operations"""
  document_id: str
  version_num: int
  status: str
  message: str