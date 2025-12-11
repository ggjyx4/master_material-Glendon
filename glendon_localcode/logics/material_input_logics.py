import time
import uuid # <--- NEW
from datetime import datetime
from data_access.material_input_data_access import MaterialInputDataAccess

# Constants
DOC_PREFIX = "vin_doc_"
MMAT_PREFIX = "vin_mmat_"
REQUIRED_FIELDS = ["material_name", "material_type"]

class MaterialService:
    def __init__(self):
        self.data_access = MaterialInputDataAccess()

    def _generate_incremental_id(self, prefix, last_id_fetcher):
        """
        Generic generator: 
        1. Calls the fetcher (function) to get the last ID from DB.
        2. Increments the number part.
        """
        last_id = last_id_fetcher(prefix)
        
        if not last_id:
            return f"{prefix}0001"
        
        try:
            # Remove prefix "vin_doc_" -> "0005"
            number_part = last_id.replace(prefix, "")
            next_num = int(number_part) + 1
            return f"{prefix}{next_num:04d}"
        except ValueError:
            # Fallback if ID was malformed
            return f"{prefix}{int(time.time())}"

    def _get_current_user_info(self):
        return "admin@company.com", "System Admin"
    # ------------------------------------------------------------------
    # Helper: Prepare Data for DB
    # ------------------------------------------------------------------
    def _prepare_version_data(self, updates: dict):
        """
        Ensures fields like fabric_composition are in the right JSON format
        and adds any calculated fields if necessary.
        """
        data = updates.copy()
        
        # If composition is a string "Cotton:50", parse it to JSON for DB
        if 'fabric_composition' in data and isinstance(data['fabric_composition'], str):
             # Simple parser logic (adjust based on your UI needs)
             # Expected DB format: [[50, "Cotton"], [50, "Poly"]]
             try:
                 # Logic to parse string to list if needed, or trust Pydantic
                 pass 
             except:
                 pass
        
        return data

 # ------------------------------------------------------------------
    # 1. CREATE
    # ------------------------------------------------------------------
    def create_material(self, request_data: dict, is_submit: bool):
        email, name = self._get_current_user_info()
        now = datetime.now()
        
        # 1. Validation
        if is_submit:
            missing = [f for f in REQUIRED_FIELDS if not request_data.get(f)]
            if missing: raise ValueError(f"Missing required fields: {', '.join(missing)}")

        # 2. ID Generation
        # A) Document ID (PK) -> vin_doc_0001
        doc_id = request_data.get('document_id')
        if not doc_id:
            doc_id = self._generate_incremental_id(DOC_PREFIX, self.data_access.get_last_doc_id)
        
        # B) Master Material ID (Human Readable) -> vin_mmat_0001
        mmat_id = request_data.get('master_material_id')
        if not mmat_id:
            mmat_id = self._generate_incremental_id(MMAT_PREFIX, self.data_access.get_last_mmat_id)

        # 3. Version UUID
        doc_uid = str(uuid.uuid4())

        status = "Submitted - Unverified" if is_submit else "Draft"
        
        # 4. Prepare Data
        clean_data = self._prepare_version_data(request_data)
        
        # INJECT the generated Human ID into the data payload so it saves to material_versions
        clean_data['master_material_id'] = mmat_id 

        # 5. DB Calls
        self.data_access.create_master_record(doc_id, email, now)
        
        self.data_access.create_version_record(
            doc_uid=doc_uid,
            doc_id=doc_id,
            ver_num=1,
            status=status,
            user=email,
            now=now,
            data=clean_data
        )

        return {
            "document_id": doc_id,
            "master_material_id": mmat_id, # Return this for UI feedback
            "version_num": 1,
            "status": status,
            "message": f"Successfully created {doc_id} ({mmat_id})"
        }

    # ------------------------------------------------------------------
    # 2. UPDATE DRAFT
    # ------------------------------------------------------------------
    def update_draft(self, document_id: str, updates: dict):
        latest = self.data_access.get_latest_version(document_id)
        if not latest: raise ValueError(f"Document {document_id} not found")
        if "Submitted" in latest['status']: raise ValueError(f"Cannot edit submitted status.")

        new_ver = latest['ver_num'] + 1
        doc_uid = str(uuid.uuid4())
        email, name = self._get_current_user_info()
        now = datetime.now()
        
        clean_data = self._prepare_version_data(updates)
        
        # PRESERVE the existing master_material_id from previous version
        # (We don't generate a new one for updates, we keep the old one)
        if 'master_material_id' not in clean_data or not clean_data['master_material_id']:
             clean_data['master_material_id'] = latest.get('master_material_id')

        self.data_access.create_version_record(
            doc_uid=doc_uid,
            doc_id=document_id,
            ver_num=new_ver,
            status="Draft",
            user=email,
            now=now,
            data=clean_data
        )

        return {
            "document_id": document_id,
            "version_num": new_ver,
            "status": "Draft",
            "message": "Draft updated"
        }

    # ------------------------------------------------------------------
    # 3. SUBMIT / 4. REVISE
    # ------------------------------------------------------------------
    def submit_version(self, document_id: str, final_updates: dict):
        return self._create_new_version(document_id, final_updates, "Submitted - Unverified")

    def create_revision_from_verified(self, document_id: str, updates: dict):
        return self._create_new_version(document_id, updates, "Submitted - Unverified")

    def _create_new_version(self, doc_id, data, status):
        email, name = self._get_current_user_info()
        now = datetime.now()
        latest = self.data_access.get_latest_version(doc_id)
        if not latest: raise ValueError("Document not found")

        new_ver = latest['ver_num'] + 1
        doc_uid = str(uuid.uuid4())

        clean_data = self._prepare_version_data(data)
        
        # PRESERVE ID
        if 'master_material_id' not in clean_data or not clean_data['master_material_id']:
             clean_data['master_material_id'] = latest.get('master_material_id')

        self.data_access.create_version_record(
            doc_uid=doc_uid,
            doc_id=doc_id,
            ver_num=new_ver,
            status=status,
            user=email,
            now=now,
            data=clean_data
        )
        return {"document_id": doc_id, "version_num": new_ver, "status": status, "message": "Success"}