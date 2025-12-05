import anvil.server
from datetime import datetime
from typing import Optional, List, Any, Dict
from pydantic import BaseModel, Field

class MaterialCard(BaseModel):
  document_id: str
  master_material_id: str
  ref_id: str
  material_name: str
  material_type: str
  fabric_composition: str
  weight: str
  supplier: str
  cost_per_unit: str
  verification_status: str
  ver_num: str

class ListMaterialCardsRequest(BaseModel):
  statuses: Optional[List[str]] = Field(
    None, 
    description="List of statuses to include. Defaults to active statuses if empty.",
    example=["Draft", "Submitted - Verified"]
  )
