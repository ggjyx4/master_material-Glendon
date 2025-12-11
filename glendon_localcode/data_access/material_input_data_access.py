from data_access.base import BaseRepository
from datetime import datetime
import json

class MaterialInputDataAccess(BaseRepository):
    def __init__(self):
        super().__init__('master_materials') 
    
    # --- ID GENERATION ---
    def get_last_auto_id(self, prefix):
        # Finds the highest ID that starts with the given prefix
        query = """
            SELECT document_id 
            FROM master_materials 
            WHERE document_id LIKE %s 
            ORDER BY LENGTH(document_id) DESC, document_id DESC 
            LIMIT 1
        """
        result = self.fetch_one(query, (f"{prefix}%",))
        return result['document_id'] if result else None
    
    def get_last_mmat_id(self, prefix):
        query = """
            SELECT master_material_id FROM material_versions 
            WHERE master_material_id LIKE %s 
            ORDER BY LENGTH(master_material_id) DESC, master_material_id DESC 
            LIMIT 1
        """
        result = self.fetch_one(query, (f"{prefix}%",))
        return result['master_material_id'] if result else None

   # ---------------------------------------------------------
    # READ Methods
    # ---------------------------------------------------------
    def get_latest_version(self, doc_id: str):
        query = "SELECT * FROM material_versions WHERE document_id = %s ORDER BY ver_num DESC LIMIT 1"
        return self.fetch_one(query, (doc_id,))

    # ---------------------------------------------------------
    # WRITE Methods
    # ---------------------------------------------------------
    def create_master_record(self, doc_id, user_email, now):
        # Initialize empty arrays for history
        query = """
            INSERT INTO master_materials (
                document_id, created_at, created_by, current_version, 
                version_history, version_history_uid
            )
            VALUES (%s, %s, %s, 1, '[]'::jsonb, '[]'::jsonb)
            ON CONFLICT (document_id) DO NOTHING
            RETURNING document_id
        """
        self.execute(query, (doc_id, now, user_email))
        return {"document_id": doc_id}

    def create_version_record(self, doc_uid, doc_id, ver_num, status, user, now, data: dict):
        # 1. Handle JSON Fields for SQL Insert
        fabric_comp_json = data.get('fabric_composition')
        if isinstance(fabric_comp_json, list):
            fabric_comp_json = json.dumps(fabric_comp_json)
        
        # 2. INSERT into Version Table
        query_insert = """
            INSERT INTO material_versions (
                document_uid, document_id, ver_num, status, change_description,
                created_at, created_by,
                ref_id, master_material_id, supplier_name, country_of_origin,
                material_name, material_type,
                unit_of_measurement, fabric_composition, generic_material_composition,
                fabric_roll_width, fabric_cut_width, fabric_cut_width_no_shrinkage,
                weight_per_unit, weight_uom, generic_material_size,
                weft_shrinkage, werp_shrinkage, estimated_logistics_lead_time,
                original_cost_per_unit, native_cost_currency,
                supplier_selling_tolerance, refundable_tolerance, effective_cost_per_unit,
                vietnam_vat_rate, refundable_vat, import_duty, refundable_import_duty,
                shipping_term, logistics_rate, logistics_fee_per_unit, landed_cost_per_unit
            )
            VALUES (
                %s, %s, %s, %s, %s,
                %s, %s,
                %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
        """
        
        insert_params = (
            doc_uid, doc_id, ver_num, status, data.get('change_description', ''),
            now, user,
            data.get('ref_id'), data.get('master_material_id'), data.get('supplier_name'), data.get('country_of_origin'),
            data.get('material_name'), data.get('material_type'),
            data.get('unit_of_measurement'), fabric_comp_json, data.get('generic_material_composition'),
            data.get('fabric_roll_width'), data.get('fabric_cut_width'), data.get('fabric_cut_width_no_shrinkage'),
            data.get('weight_per_unit'), data.get('weight_uom'), data.get('generic_material_size'),
            data.get('weft_shrinkage'), data.get('werp_shrinkage'), data.get('estimated_logistics_lead_time'),
            data.get('original_cost_per_unit'), data.get('native_cost_currency'),
            data.get('supplier_selling_tolerance'), data.get('refundable_tolerance'), data.get('effective_cost_per_unit'),
            data.get('vietnam_vat_rate'), data.get('refundable_vat'), data.get('import_duty'), data.get('refundable_import_duty'),
            data.get('shipping_term'), data.get('logistics_rate'), data.get('logistics_fee_per_unit'), data.get('landed_cost_per_unit')
        )
        self.execute(query_insert, insert_params)

        # 3. PREPARE JSON OBJECT FOR HISTORY
        # We reconstruct the object to store inside the master JSON array
        # Note: We must serialize datetime objects to string
        version_obj = {
            "document_uid": doc_uid,
            "ver_num": ver_num,
            "master_material_id": data.get('master_material_id'),
            "created_at": now.isoformat(),
            "status": status,
            "material_name": data.get('material_name'),
            "cost": data.get('original_cost_per_unit'),
            "currency": data.get('native_cost_currency')
            # Add other fields here if you want them in the history summary
        }

        # 4. UPDATE Master Table (Append to History Arrays)
        # Using Postgres '||' operator to append to JSONB array
        query_update_master = """
            UPDATE master_materials
            SET 
                -- Append full object to history
                version_history = version_history || %s::jsonb,
                -- Append UUID to uid list
                version_history_uid = version_history_uid || %s::jsonb,
                
                -- Update Current Pointers
                current_version = %s,
                current_version_uid = %s,
                submitted_at = CASE WHEN %s LIKE 'Submitted%%' THEN %s ELSE submitted_at END,
                submitted_by = CASE WHEN %s LIKE 'Submitted%%' THEN %s ELSE submitted_by END
            WHERE document_id = %s
        """
        
        self.execute(query_update_master, (
            json.dumps([version_obj]),  # Wrap in list to append
            json.dumps([doc_uid]),      # Wrap in list to append
            ver_num, 
            doc_uid,
            status, now,
            status, user,
            doc_id
        ))

        return {"master_id": doc_id, "version": ver_num, "status": status}