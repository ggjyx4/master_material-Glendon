import anvil.server
from .data_access.material_detail_data_access import MaterialDetailDataAccess
from .schemas.material_detail_schemas import MaterialDetailResponse

class material_detail_logics:
    def _get(row, key, default=None):
        """Safely get a value from a row"""
        try:
            val = row[key]
            return val if val is not None else default
        except Exception:
            return default

    def build_material_detail(version_row) -> dict:
        # Business Logic: Calculate Cost Display
        ocpu = _get(version_row, "original_cost_per_unit")
        nccy = _get(version_row, "native_cost_currency")
        cost_display = f"{ocpu} {nccy}" if (ocpu is not None and nccy) else ""

        # Return Dict matching the Schema
        return {
            "document_id": _get(version_row, "document_id", " "),
            "ver_num": str(_get(version_row, "ver_num", " ")), 
            "master_material_id": _get(version_row, "master_material_id", " "),
            "name": _get(version_row, "name", " "),
            "ref_id": _get(version_row, "ref_id", " "),
            "material_type": _get(version_row, "material_type", " "),
            "supplier": _get(version_row, "supplier_name", " "),
            "country_of_origin": _get(version_row, "country_of_origin", " "),
            "created_by": _get(version_row, "created_by", " "),
            "created_at": _get(version_row, "created_at", " "),
            "fabric_composition": _get(version_row, "fabric_composition", " "),
            "weight_per_unit": _get(version_row, "weight_per_unit", " "),
            "fabric_roll_width": _get(version_row, "fabric_roll_width", " "),
            "fabric_cut_width": _get(version_row, "fabric_cut_width", " "),
            "original_cost_per_unit": ocpu,
            "cost_display": cost_display,
            "unit_of_measurement": _get(version_row, "unit_of_measurement", " "),
            "verification_status": _get(version_row, "status", "Draft"),
            "updated_at": _get(version_row, "updated_at"),
            "submitted_at": _get(version_row, "submitted_at"),
            "last_verified_date": _get(version_row, "last_verified_date"),
        }

    def build_technical_detail(version_row) -> dict:
        return {
            "fabric_composition": _get(version_row, "fabric_composition"),
            "fabric_roll_width": _get(version_row, "fabric_roll_width"),
            "fabric_cut_width": _get(version_row, "fabric_cut_width"),
            "fabric_cut_width_no_shrinkage": _get(version_row, "fabric_cut_width_no_shrinkage"),
            "weight_per_unit": _get(version_row, "weight_per_unit"),
            "weft_shrinkage": _get(version_row, "weft_shrinkage"),
            "werp_shrinkage": _get(version_row, "werp_shrinkage"),
        }

    def build_cost_detail(version_row) -> dict:
        return {
            "original_cost_per_unit": _get(version_row, "original_cost_per_unit"),
            "currency": _get(version_row, "native_cost_currency"),
            "supplier_tolerance": _get(version_row, "supplier_selling_tolerance"),
            "effective_cost": _get(version_row, "effective_cost_per_unit"),
            "vat": _get(version_row, "vietnam_vat_rate"),
            "import_duty": _get(version_row, "import_duty"),
            "logistics_rate": _get(version_row, "logistics_rate"),
            "landed_cost": _get(version_row, "landed_cost_per_unit"),
        }

    def build_version_history(version_rows) -> list:
        # Business Logic: Sorting
        version_rows.sort(key=lambda v: v['ver_num'])
        
        return [
            {
                "ver_num": int(v['ver_num']),
                "submitted_by": v.get('submitted_by', '') or '',
                "submitted_at": v.get('submitted_at', None),
                "change_description": v.get('change_description', '') or ''
            }
            for v in version_rows
        ]

    def build_full_row(version_row) -> dict:
        result = dict(version_row)
        result['verification_status'] = version_row['status']
        return result