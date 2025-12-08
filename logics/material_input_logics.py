import uuid
from datetime import datetime
import anvil.users
from .data_access.material_input_data_access import MaterialInputDataAccess 
from .schemas.material_input_schemas import CreateMaterialRequest, MaterialResponse, UpdateDraftRequest, SubmitVersionRequest, EditVerifiedRequest
# Constants
DOC_PREFIX = "vin_mmat_"
REQUIRED_FIELDS = ["material_name", "material_type", "supplier_name"]

class MaterialService:

    def _generate_next_document_id(self):
        """Domain logic to calculate next ID"""
        # Note: If concurrent users is high, move this logic to a SQL query or counter table
        all_rows = MaterialInputDataAccess.get_all_masters()
        numbers = []
        for r in all_rows:
            try:
                num = int(r['document_id'].replace(DOC_PREFIX, ''))
                numbers.append(num)
            except (ValueError, AttributeError):
                continue

        next_num = (max(numbers) + 1) if numbers else 1
        return f"{DOC_PREFIX}{next_num:04d}"

    def _get_current_user_info(self):
        user = anvil.users.get_user()
        if user:
            return user['email'], user['full_name']
        return "system", "System"

    def create_material(self, request_data: dict, is_submit: bool):
        email, name = self._get_current_user_info()
        now = datetime.now()
        
        # 1. Validation for Immediate Submit
        if is_submit:
            missing = [f for f in REQUIRED_FIELDS if not request_data.get(f)]
            if missing:
                raise Exception(f"Cannot submit. Missing required fields: {', '.join(missing)}")

        # 2. Prep IDs
        doc_id = self._generate_next_document_id()
        doc_uid = str(uuid.uuid4())
        status = "Submitted - Unverified" if is_submit else "Draft"
        creator = email if is_submit else name # Logic from your original code (email vs name)

        # 3. DB Operations
        master_row = MaterialInputDataAccess.create_master_record(doc_id, doc_uid, creator, now)
        
        MaterialInputDataAccess.create_version_record(
            master_row=master_row,
            doc_id=doc_id,
            doc_uid=doc_uid,
            ver_num=1,
            status=status,
            user=creator,
            now=now,
            data=request_data
        )

        return {
            "document_id": doc_id,
            "version_num": 1,
            "status": status,
            "message": "Material created successfully"
        }

    def update_draft(self, document_id: str, updates: dict):
        # 1. Fetch
        master = MaterialInputDataAccess.get_master_by_id(document_id)
        if not master:
            raise Exception(f"Document {document_id} not found")

        version = master['current_version']
        
        # 2. Logic Check
        if version['status'] != "Draft":
            raise Exception(f"Cannot edit {document_id}. Status is '{version['status']}', must be 'Draft'.")

        # 3. Update
        for k, v in updates.items():
            version[k] = v

        return {
            "document_id": document_id,
            "version_num": version['ver_num'],
            "status": "Draft",
            "message": "Draft updated successfully"
        }

    def submit_version(self, document_id: str, final_updates: dict):
        email, name = self._get_current_user_info()
        
        # 1. Fetch
        master = MaterialInputDataAccess.get_master_by_id(document_id)
        if not master:
            raise Exception("Document not found")
        version = master['current_version']

        # 2. Logic Checks
        if version['status'] != "Draft":
            raise Exception("Only Drafts can be submitted")

        # Apply updates
        if final_updates:
            for k, v in final_updates.items():
                version[k] = v
        
        # Check Requirements
        missing = [f for f in REQUIRED_FIELDS if not version[f]]
        if missing:
            raise Exception(f"Missing required fields: {', '.join(missing)}")

        # 3. Transition
        now = datetime.now()
        version['status'] = "Submitted - Unverified"
        version['submitted_at'] = now
        version['submitted_by'] = name
        master['submitted_at'] = now
        master['submitted_by'] = name

        return {
            "document_id": document_id,
            "version_num": version['ver_num'],
            "status": "Submitted - Unverified",
            "message": "Version submitted for verification"
        }

    def create_revision_from_verified(self, document_id: str, updates: dict):
        email, name = self._get_current_user_info()
        
        # 1. Fetch
        master = MaterialInputDataAccess.get_master_by_id(document_id)
        if not master: 
            raise Exception("Document not found")

        old_v = master['current_version']
        
        # 2. Logic Checks
        if old_v['status'] != "Submitted - Verified":
            raise Exception("Can only revise Verified documents")

        # 3. Prepare Data (Cloning Logic)
        # Note: We rely on the LINKED row for version number, not master column
        new_ver_num = old_v['ver_num'] + 1
        new_uid = str(uuid.uuid4())
        now = datetime.now()

        exclude_fields = {
            "document_id", "document_uid", "ver_num", "status", 
            "created_at", "submitted_at", "submitted_by",
            "last_verified_date", "last_verified_by"
        }
        
        # Clone old data
        cloned_data = {
            k: v for k, v in dict(old_v).items() 
            if k not in exclude_fields and not k.startswith("_")
        }
        
        # Overlay new updates
        if updates:
            cloned_data.update(updates)

        # 4. Create New Version
        MaterialInputDataAccess.create_version_record(
            master_row=master,
            doc_id=document_id,
            doc_uid=new_uid,
            ver_num=new_ver_num,
            status="Submitted - Unverified",
            user=name,
            now=now,
            data=cloned_data
        )

        return {
            "document_id": document_id,
            "version_num": new_ver_num,
            "status": "Submitted - Unverified",
            "message": "New version created and submitted"
        }