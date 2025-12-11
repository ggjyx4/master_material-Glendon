from schemas.material_detail_schemas import MaterialDetailResponse

class MaterialDetailLogics:
    
    def _get(self, row, key, default=None):
        if not row: return default
        return row.get(key, default)

    def build_material_detail(self, row) -> dict:
        ocpu = self._get(row, "original_cost_per_unit")
        nccy = self._get(row, "native_cost_currency")
        cost_display = f"{ocpu} {nccy}" if (ocpu and nccy) else ""

        return {
            # Meta
            "document_id": self._get(row, "document_id", " "),
            "document_uid": self._get(row, "document_uid"), # <--- NEW
            "ver_num": self._get(row, "ver_num"), 
            "status": self._get(row, "status", "Draft"),
            
            # Header
            "master_material_id": self._get(row, "master_material_id", " "),
            "material_name": self._get(row, "material_name", " "),
            "ref_id": self._get(row, "ref_id", " "),
            "material_type": self._get(row, "material_type", " "),
            "supplier_name": self._get(row, "supplier_name", " "),
            "country_of_origin": self._get(row, "country_of_origin", " "),
            
            # Media
            "qr_id": self._get(row, "qr_id"), # <--- NEW
            "hanger_pdf_id": self._get(row, "hanger_pdf_id"), # <--- NEW
            "picture_id": self._get(row, "picture_id"), # <--- NEW

            # Audit
            "created_by": self._get(row, "created_by", " "),
            "created_at": self._get(row, "created_at"),
            "submitted_at": self._get(row, "submitted_at"),
            "last_verified_date": self._get(row, "last_verified_date"),
            
            # Summary
            "cost_display": cost_display,
            "verification_status": self._get(row, "status"),
        }

    def build_technical_detail(self, row) -> dict:
        return {
            "unit_of_measurement": self._get(row, "unit_of_measurement"),
            "fabric_composition": self._get(row, "fabric_composition"), # Passes JSON straight through
            "generic_material_composition": self._get(row, "generic_material_composition"), # <--- NEW
            
            "fabric_roll_width": self._get(row, "fabric_roll_width"),
            "fabric_cut_width": self._get(row, "fabric_cut_width"),
            "fabric_cut_width_no_shrinkage": self._get(row, "fabric_cut_width_no_shrinkage"),
            
            "weight_per_unit": self._get(row, "weight_per_unit"),
            "weight_uom": self._get(row, "weight_uom"), # <--- NEW
            "generic_material_size": self._get(row, "generic_material_size"), # <--- NEW
            
            "weft_shrinkage": self._get(row, "weft_shrinkage"),
            "werp_shrinkage": self._get(row, "werp_shrinkage"),
            
            "estimated_logistics_lead_time": self._get(row, "estimated_logistics_lead_time"), # <--- NEW
        }

    def build_cost_detail(self, row) -> dict:
        return {
            "original_cost_per_unit": self._get(row, "original_cost_per_unit"),
            "native_cost_currency": self._get(row, "native_cost_currency"),
            
            "supplier_selling_tolerance": self._get(row, "supplier_selling_tolerance"),
            "refundable_tolerance": self._get(row, "refundable_tolerance"), # <--- NEW
            "effective_cost_per_unit": self._get(row, "effective_cost_per_unit"),
            
            "vietnam_vat_rate": self._get(row, "vietnam_vat_rate"),
            "refundable_vat": self._get(row, "refundable_vat"), # <--- NEW
            
            "import_duty": self._get(row, "import_duty"),
            "refundable_import_duty": self._get(row, "refundable_import_duty"), # <--- NEW
            
            "shipping_term": self._get(row, "shipping_term"), # <--- NEW
            "logistics_rate": self._get(row, "logistics_rate"),
            "logistics_fee_per_unit": self._get(row, "logistics_fee_per_unit"), # <--- NEW
            
            "landed_cost_per_unit": self._get(row, "landed_cost_per_unit"),
        }

    def build_version_history(self, rows) -> list:
        if not rows: return []
        rows.sort(key=lambda x: x.get('ver_num', 0))
        return [
            {
                "ver_num": r.get('ver_num'),
                "submitted_by": r.get('submitted_by', ''),
                "submitted_at": r.get('submitted_at'),
                "change_description": r.get('change_description', '')
            }
            for r in rows
        ]