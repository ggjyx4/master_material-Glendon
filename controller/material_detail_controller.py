import anvil.server
from .api_framework import APIEndpoint
from typing import List, Dict, Any
from schemas.material_detail_schema import MaterialDetailRequest, MaterialDetailResponse, TechnicalDetailResponse, CostDetailResponse
from data_access.material_detail_data_access import MaterialDetailDataAccess
from logics.material_detail_logics import MaterialDetailLogics

# ------------------------------------------------------------------
data_access = MaterialDetailDataAccess()
logics = MaterialDetailLogics()
# ------------------------------------------------------------------

@anvil.server.route("/get_material_detail")
@APIEndpoint(
  name="get_material_detail",
  request_model=MaterialDetailRequest,
  response_model=MaterialDetailResponse,
  summary="Get Material Dashboard Details",
  tags=["Materials", "Dashboard"]
)
def get_material_detail(request: MaterialDetailRequest):
    # 1. Data Access
    version_row = data_access.get_current_version_row(request.document_id)
    # 2. Logic & Transformation
    response_data = logics.build_material_detail(version_row)
    # 3. Response
    return response_data

# ------------------------------------------------------------------

@anvil.server.route("/get_technical_detail")
@APIEndpoint(
  name="get_technical_detail",
  request_model=schemas.MaterialIDRequest,
  response_model=schemas.TechnicalDetailResponse,
  summary="Get Technical Specifications",
  tags=["Materials", "Technical"]
)
def get_technical_detail(request: schemas.MaterialIDRequest):
    version_row = data_access.get_current_version_row(request.document_id)
    return logics.build_technical_detail(version_row)

# ------------------------------------------------------------------

@anvil.server.route("/get_cost_detail")
@APIEndpoint(
  name="get_cost_detail",
  request_model=schemas.MaterialIDRequest,
  response_model=schemas.CostDetailResponse,
  summary="Get Cost Breakdown",
  tags=["Materials", "Financial"]
)
def get_cost_detail(request: schemas.MaterialIDRequest):
    version_row = data_access.get_current_version_row(request.document_id)
    return logics.build_cost_detail(version_row)

# ------------------------------------------------------------------

@anvil.server.route("/get_version_history")
@APIEndpoint(
  name="get_version_history",
  request_model=schemas.MaterialIDRequest,
  response_model=List[schemas.VersionHistoryItem],
  summary="Get Version History",
  tags=["Materials", "History"]
)
def get_version_history(request: schemas.MaterialIDRequest):
    history_rows = data_access.get_version_history_rows(request.document_id)
    return logics.build_version_history(history_rows)

# ------------------------------------------------------------------

@anvil.server.route("/get_material_full_row")
@APIEndpoint(
  name="get_material_full_row",
  request_model=schemas.MaterialIDRequest,
  response_model=Dict[str, Any],
  summary="Get Full Material Row",
  tags=["Materials", "Internal"]
)
def get_material_full_row(request: schemas.MaterialIDRequest):
    try:
        version_row = data_access.get_current_version_row(request.document_id)
        return logics.build_full_row(version_row)
    except Exception:
        # Return empty dict if not found (matching original logic)
        return {}