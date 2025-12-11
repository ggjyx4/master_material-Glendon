from typing import Optional, List, Tuple
from enum import Enum
from datetime import datetime
from pydantic import BaseModel, Field
from decimal import Decimal
from typing import Literal

class Master_material_version(BaseModel):
  # meta data
  document_id: str # submittable type hence once update create new role keeping cost_sheet_id unchanged
  document_uid: str
  ver_num: int
  change_description: str
  created_at: datetime
  created_by: User
  submitted_at: datetime
  submitted_by: User
  last_verified_date: datetime # only sourcing or buying staff can verified the information => before buying should double check
  last_verified_by: User
  ref_id: str # id from the supplier
  master_material_id: str # human-readable id
  status: Literal["Draft", "Submitted - Unverified", "Submitted - Verified"]
  supplier: Optional[Supplier] # only optional if the status is Draft
  supplier_name: str
  country_of_origin: Literal["Vietnam", "China"]
  estimated_logistics_lead_time: int # based on the country of origin
  material_name: str
  material_type: Material_type
  qr_id: str # link to QR code table
  hanger_pdf_id: str # link to PDF table
  picture_id: str # link to picture table

  # technical specifications
  unit_of_measurement: Literal["meter", "piece"]
  fabric_composition: Optional[list[tuple[float, Material_composition]]] # only for fabric
  generic_material_composition: Optional[str] # button: plastic vs metal
  fabric_roll_width: Optional[float] = Field(ge=0, le=3) # fabric width cannot be negative and greater than 3 METERS
  fabric_cut_width: Optional[float] = Field(ge=0, le=3) # fabric width cannot be negative and greater than 3 METERS
  fabric_cut_width_no_shrinkage: Optional[float] = Field(ge=0, le=3) # fabric width cannot be negative and greater than 3 METERS
  weight_per_unit: float # ideally can validate per material type e.g. fabric ok with float but button should be int
  weight_uom: Material_weight_uom # gram per piece (trim), gram per square meter (fabric)
  generic_material_size: str # ideally... button: 20L 20 Ligne, 24L, etc.
  weft_shrinkage: Optional[float] = Field(ge=-1, le=1)
  werp_shrinkage: Optional[float] = Field(ge=-1, le=1)

  # cost (basic)
  original_cost_per_unit: float
  native_cost_currency: Literal["USD", "VND", "RMB"] # should set up a way to record exchange rates used in cost calculation
  supplier_selling_tolerance: float = Field(ge=0, le=1)
  refundable_tolerance: bool
  effective_cost_per_unit: float # calculated by multiplying with supplier tolerance
  # cost (advanced) -> help to estimate only
  vietnam_vat_rate: Optional[Literal["8%", "10%"]]
  refundable_vat: bool
  import_duty: Optional[float] = Field(ge=0, le=1)
  refundable_import_duty: bool
  shipping_term: Literal["EXW", "FOB", "DDP"]
  logistics_rate: Optional[float] = Field(ge=0, le=1) # one option is to calculate per estimated % rate
  logistics_fee_per_unit: Optional[float] # another option is to calculate using net weight & gross weight, assuming slow option
  landed_cost_per_unit: float

class Master_material(BaseModel):
  document_id: str # submittable type hence once update create new role keeping cost_sheet_id unchanged
  current_version: int # Link to ver_num at master_material_version
  current_version_uid: str
  version_history: list[Master_material_version]
  version_history_uid: list[document_uid]
  created_at: datetime
  created_by: User
  submitted_at: datetime
  submitted_by: User
  last_verified_date: datetime
  last_verified_by : User

class Material_SKU(BaseModel):
  id: str
  ref_id: str
  master_material: Master_material
  color: Optional[str]
  size: Optional[str]
  qr_data: str
  sku_cost_override: float # expect same as material cost, but sometimes colors or size comes with a different cost hence used this overriden cost