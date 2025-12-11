from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel, Field

class MaterialCard(BaseModel):
  document_id: str
  master_material_id: Optional[str]
  ref_id: Optional[str]
  material_name: Optional[str]
  material_type: Optional[str]
  
  # Thumbnail / Summary
  fabric_composition: Optional[str] # Human readable summary of the JSON
  weight: Optional[str] # Combined value + UOM
  supplier_name: Optional[str]
  cost_per_unit: Optional[str] # Formatted currency string
  
  verification_status: Optional[str]
  ver_num: int
  picture_id: Optional[str]

class ListMaterialCardsRequest(BaseModel):
  statuses: Optional[List[str]] = Field(
    None, 
    description="List of statuses to include. Defaults to active statuses if empty.",
    example=["Draft", "Submitted - Verified"]
  )