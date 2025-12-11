from schemas.material_card_schemas import MaterialCard

def _format_composition_for_card(comp_data):
    """
    Converts JSONB composition data into a short string for the card.
    Input: [[50, "Cotton"], [50, "Poly"]] OR [{"name":"Cotton", "percentage":50}]
    Output: "Cotton 50% | Poly 50%"
    """
    if not comp_data: return " "
    
    # If it's already a string, return it
    if isinstance(comp_data, str): return comp_data
    
    try:
        # Handle List of Lists [[50, "Cotton"]]
        if isinstance(comp_data, list) and len(comp_data) > 0 and isinstance(comp_data[0], list):
            return " | ".join([f"{item[1]} {item[0]}%" for item in comp_data])
            
        # Handle List of Dicts [{"name": "Cotton", "percentage": 50}]
        if isinstance(comp_data, list) and len(comp_data) > 0 and isinstance(comp_data[0], dict):
             return " | ".join([f"{item.get('name')} {item.get('percentage')}%" for item in comp_data])
    except:
        return "Complex Composition"
        
    return " "

def _format_single_card(row):
    # Logic: Format Weight
    wpu = row.get('weight_per_unit')
    wuom = row.get('weight_uom') 
    weight = f"{wpu} {wuom}" if (wpu and wuom) else str(wpu or "")

    # Logic: Format Cost
    ocpu = row.get('original_cost_per_unit')
    nccy = row.get('native_cost_currency')
    cost = f"{ocpu} {nccy}" if (ocpu and nccy) else ""

    return {
        "document_id": row.get('document_id') or " ", 
        "master_material_id": row.get('master_material_id') or " ", # Use the human readable ID
        "ref_id": row.get('ref_id') or " ",
        "material_name": row.get('material_name') or "Unknown Material",
        "material_type": row.get('material_type') or " ",
        
        # New Helper for Composition
        "fabric_composition": _format_composition_for_card(row.get('fabric_composition')),
        
        "weight": weight,
        "supplier_name": row.get('supplier_name') or " ",
        "cost_per_unit": cost,
        "verification_status": row.get('status') or "Draft",
        "ver_num": row.get('ver_num'),
        "picture_id": row.get('picture_id') # <--- NEW
    }

def process_material_cards(sql_rows, allowed_statuses):
    cards = []
    for row in sql_rows:
        status = row.get('status')
        # Logic: If statuses are provided, filter. If None, show all.
        if allowed_statuses and status not in allowed_statuses:
            continue

        formatted_card = _format_single_card(row)
        cards.append(formatted_card)
        
    return cards