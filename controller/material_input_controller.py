import anvil.server
from .api_framework import APIEndpoint
from schemas.material_input_schemas import CreateMaterialRequest, MaterialResponse, UpdateDraftRequest, SubmitVersionRequest, EditVerifiedRequest
from logics.material_input_logics import MaterialService
from data_access.material_input_data_access import MaterialInputDataAccess

material_service = MaterialService()

@anvil.server.route("/create_and_submit", methods=["POST"])
@APIEndpoint(
  name="create_and_submit_material",
  request_model=CreateMaterialRequest,
  response_model=MaterialResponse,
  summary="Create & Submit Immediately",
  tags=["Material Input"]
)
def create_and_submit_material(request: CreateMaterialRequest):
    return material_service.create_material(
        request_data=request.model_dump(exclude_none=True), 
        is_submit=True
    )

@anvil.server.route("/create_material_draft", methods=["POST"])
@APIEndpoint(
  name="create_material_draft",
  request_model=CreateMaterialRequest,
  response_model=MaterialResponse,
  summary="Create New Draft",
  tags=["Material Input"]
)
def create_material_draft(request: CreateMaterialRequest):
    return material_service.create_material(
        request_data=request.model_dump(exclude_none=True), 
        is_submit=False
    )

@anvil.server.route("/update_draft", methods=["POST"])
@APIEndpoint(
  name="update_draft",
  request_model=UpdateDraftRequest,
  response_model=MaterialResponse,
  summary="Update Existing Draft",
  tags=["Material Input"]
)
def update_draft(request: UpdateDraftRequest):
    return material_service.update_draft(
        document_id=request.document_id,
        updates=request.model_dump(exclude={'document_id'}, exclude_none=True)
    )

@anvil.server.route("/submit_version", methods=["POST"])
@APIEndpoint(
  name="submit_version",
  request_model=SubmitVersionRequest,
  response_model=MaterialResponse,
  summary="Submit Draft to Unverified",
  tags=["Material Input"]
)
def submit_version(request: SubmitVersionRequest):
    return material_service.submit_version(
        document_id=request.document_id,
        final_updates=request.form_data
    )

@anvil.server.route("/edit_verified", methods=["POST"])
@APIEndpoint(
  name="edit_verified",
  request_model=EditVerifiedRequest,
  response_model=MaterialResponse,
  summary="Revise Verified Document",
  tags=["Material Input"]
)
def edit_verified(request: EditVerifiedRequest):
    return material_service.create_revision_from_verified(
        document_id=request.document_id,
        updates=request.form_data
    )