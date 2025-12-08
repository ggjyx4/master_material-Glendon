import anvil.server
from .data_access.material_card_data_access import MaterialCardDataAccess
from .schemas.material_card_schemas import MaterialCardResponse


# logic.py (or a section in your server module)

def _format_single_card(master, version):
    """
    Helper Logic: Formats a single version row into a UI card dictionary.
    """
    # Logic: Format Weight
    wpu = version['weight_per_unit']
    wuom = version['weight_uom']
    weight = f"{wpu} {wuom}" if (wpu and wuom) else ""

    # Logic: Format Cost
    ocpu = version['original_cost_per_unit']
    nccy = version['native_cost_currency']
    cost = f"{ocpu} {nccy}" if (ocpu and nccy) else ""

    # Logic: Build Dictionary
    return {
        "document_id": master['document_id'] or " ",
        "master_material_id": version['master_material_id'] or " ",
        "ref_id": version['ref_id'] or " ",
        "material_name": version['name'] or " ",
        "material_type": version['material_type'] or " ",
        "fabric_composition": version['fabric_composition'] or " ",
        "weight": weight or " ",
        "supplier": version['supplier_name'] or " ",
        "cost_per_unit": cost or " ",
        "verification_status": version['status'] or "Draft",
        "ver_num": str(version['ver_num']) if version['ver_num'] else " ",
    }

def process_material_cards(masters, allowed_statuses):
    """
    Business Logic: Filters and transforms a list of master materials.
    """
    cards = []
    
    for master in masters:
        # 1. Safety Check
        version = master['current_version']
        if not version:
            continue

        # 2. Filter Logic
        if version['status'] not in allowed_statuses:
            continue

        # 3. Transformation Logic
        formatted_card = _format_single_card(master, version)
        cards.append(formatted_card)
        
    return cards