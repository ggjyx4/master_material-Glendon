import streamlit as st
import requests
import pandas as pd
import time
import re
import uuid # For generating UIDs if needed on frontend

# -----------------------------------------------------------------------------
# 1. CONFIGURATION
# -----------------------------------------------------------------------------
API_URL = "http://api:8000"

st.set_page_config(page_title="Master Material", layout="wide", page_icon="🧶")

if 'view' not in st.session_state: st.session_state.view = 'list'
if 'selected_id' not in st.session_state: st.session_state.selected_id = None
if 'chat_history' not in st.session_state: 
    st.session_state.chat_history = [{"role": "assistant", "content": "Hello! I can help you find materials. Try typing 'Find MAT-001' or 'Show me the cost of Silk'."}]

# -----------------------------------------------------------------------------
# 2. API HELPERS
# -----------------------------------------------------------------------------
def get_api(endpoint, payload=None):
    try:
        url = f"{API_URL}{endpoint}"
        if payload is not None:
            res = requests.post(url, json=payload, timeout=5)
        else:
            res = requests.get(url, timeout=5)
        
        if res.status_code == 200:
            return res.json()
        return None
    except Exception:
        return None

# -----------------------------------------------------------------------------
# 3. LLM CHATBOX
# -----------------------------------------------------------------------------
def process_chat_query(query):
    query_upper = query.upper()
    match = re.search(r'([A-Z]+[_\-][A-Z0-9_\-]+)', query_upper)
    
    if match:
        doc_id = match.group(1)
        data = get_api("/material_details/dashboard", {"document_id": doc_id})
        
        if data:
            if "COST" in query_upper or "PRICE" in query_upper:
                return f"💰 The cost for **{data.get('name')}** ({doc_id}) is **{data.get('cost_display')}**."
            elif "SUPPLIER" in query_upper:
                return f"🏭 **{data.get('name')}** is supplied by **{data.get('supplier')}**."
            else:
                st.session_state.selected_id = doc_id 
                return f"✅ **Found it!**\n\n**Name:** {data.get('name')}\n**Status:** {data.get('verification_status')}\n**Type:** {data.get('material_type')}"
        else:
            return f"❌ I searched for ID **{doc_id}**, but it wasn't found."
            
    return "I didn't recognize a Material ID. Please specify the ID (e.g. MAT-001)."

# -----------------------------------------------------------------------------
# 4. COMPONENTS
# -----------------------------------------------------------------------------
def render_sidebar():
    with st.sidebar:
        st.title("🤖 Material Chat")
        messages = st.container(height=400)
        for msg in st.session_state.chat_history:
            messages.chat_message(msg["role"]).write(msg["content"])

        if prompt := st.chat_input("Find material by ID..."):
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            response = process_chat_query(prompt)
            st.session_state.chat_history.append({"role": "assistant", "content": response})
            st.rerun()

        st.divider()
        if st.button("🏠 Back to List", use_container_width=True):
            st.session_state.view = 'list'
            st.session_state.selected_id = None
            st.rerun()

def render_status_badge(status):
    status = status or "Draft"
    if "Verified" in status and "Unverified" not in status:
        color = "green"
    elif "Unverified" in status:
        color = "blue"
    else:
        color = "orange"
    st.markdown(f":{color}-background[{status}]")

# -----------------------------------------------------------------------------
# 5. VIEW: DASHBOARD (List)
# -----------------------------------------------------------------------------
def view_dashboard():
    st.title("🍔 Master Material")
    
    col1, col2 = st.columns([6, 1])
    with col2:
        if st.button("➕ New Material", type="primary"):
            st.session_state.view = 'create'
            st.rerun()

    materials = get_api("/material_cards/list", {"statuses": []})
    
    if not materials:
        st.info("No materials found. Database is empty.")
        return

    st.markdown("---")
    for mat in materials:
        with st.container():
            c1, c2, c3, c4, c5 = st.columns([1.5, 3, 2, 2, 1])
            with c1: 
                st.write(f"**{mat.get('document_id')}**")
                st.caption(f"Ver: {mat.get('ver_num')}")
            with c2: st.write(f"📄 {mat.get('material_name')}")
            with c3: st.write(f"🏷️ {mat.get('material_type')}")
            with c4: render_status_badge(mat.get('verification_status'))
            with c5:
                if st.button("View", key=mat['document_id']):
                    st.session_state.selected_id = mat['document_id']
                    st.session_state.view = 'detail'
                    st.rerun()
        st.divider()

# -----------------------------------------------------------------------------
# 6. VIEW: CREATE / EDIT (PROFESSIONAL UI UX)
# -----------------------------------------------------------------------------
def view_create():
    # --- HEADER & ACTIONS ---
    c1, c2 = st.columns([1, 6])
    with c1:
        if st.button("← Back", use_container_width=True):
            st.session_state.fabric_stack = []
            st.session_state.view = 'list'
            st.rerun()
    with c2:
        st.title("🧶 New Material Entry")

    if 'fabric_stack' not in st.session_state:
        st.session_state.fabric_stack = []

    # --- SECTION 1: IDENTITY ---
    st.markdown("### 1. Identity & Supplier")
    with st.container(border=True):
        c1, c2, c3 = st.columns([2, 2, 1])
        with c1:
            name = st.text_input("Material Name 🔴", placeholder="e.g., Heavy Cotton Twill", key="in_name")
            supplier = st.text_input("Supplier Name 🔴", placeholder="e.g., ABC Textiles", key="in_supplier")
        with c2:
            m_type = st.selectbox("Material Type 🔴", ["Main Fabric", "Secondary Fabric", "Trim", "Packaging"], index=0, key="in_type")
            ref_id = st.text_input("Supplier Ref ID", placeholder="e.g., SUP-2024-001", key="in_ref")
        with c3:
            country = st.selectbox("Origin", ["Vietnam", "China", "India", "Turkey", "Other"], key="in_country")
            uom = st.selectbox("UOM 🔴", ["Meter", "Yard", "Piece", "Kg"], key="in_uom")
            st.text_input("System ID", value="Auto-Generated", disabled=True)

    # --- SECTION 2: COMPOSITION BUILDER ---
    st.markdown("### 2. Composition Builder")
    with st.container(border=True):
        current_total = sum([item['pct'] for item in st.session_state.fabric_stack])
        remaining = 100.0 - current_total
        
        bar_color = "green" if current_total == 100 else ("red" if current_total > 100 else "blue")
        st.markdown(f"**Total Composition: :{bar_color}[{current_total}%]**")
        st.progress(min(current_total / 100.0, 1.0))

        c_input, c_btn = st.columns([5, 1], vertical_alignment="bottom")
        with c_input:
            ac1, ac2 = st.columns([1, 1])
            with ac1:
                val = st.number_input("Percentage", 0.0, 100.0, value=max(0.0, remaining), step=1.0, key="builder_pct", disabled=(current_total>=100))
            with ac2:
                mat = st.selectbox("Fiber", ["Cotton", "Polyester", "Elastane", "Viscose", "Linen", "Silk", "Wool", "Nylon", "Recycled Poly"], key="builder_mat", disabled=(current_total>=100))
        
        with c_btn:
            if st.button("➕ Add", use_container_width=True, disabled=(current_total>=100), key="btn_add_comp"):
                if val > 0:
                    st.session_state.fabric_stack.append({"name": mat, "pct": val})
                    st.rerun()

        if st.session_state.fabric_stack:
            st.divider()
            for i, item in enumerate(st.session_state.fabric_stack):
                rc1, rc2, rc3 = st.columns([4, 2, 1])
                with rc1: st.write(f"🧬 **{item['name']}**")
                with rc2: st.write(f"{item['pct']}%")
                with rc3:
                    if st.button("🗑️", key=f"del_{i}"):
                        st.session_state.fabric_stack.pop(i)
                        st.rerun()

    # --- SECTION 3: TECHNICAL SPECS ---
    st.markdown("### 3. Technical Specifications")
    with st.container(border=True):
        col_left, col_right = st.columns(2)
        with col_left:
            st.markdown("##### 📏 Dimensions")
            width = st.number_input("Roll Width (m)", min_value=0.0, format="%.2f", key="in_width")
            cut_width = st.number_input("Cut Width (m)", min_value=0.0, format="%.2f", key="in_cut")
            cut_width_no_shrink = st.number_input("Cut Width (no shrink)", min_value=0.0, format="%.2f", key="in_cut_ns")
            st.markdown("##### 📏 Size / Spec")
            gen_size = st.text_input("Material Size/Spec", placeholder="e.g. 20L for buttons", help="For accessories: buttons size (20L), zipper width, etc.", key="in_gen_size")

        with col_right:
            st.markdown("##### 📉 Shrinkage")
            weft = st.number_input("Weft Shrinkage", format="%.1f", key="in_weft")
            werp = st.number_input("Werp Shrinkage", format="%.1f", key="in_werp")
            st.markdown("##### ⚖️ Weight")
            weight = st.number_input("Weight per Unit 🔴", min_value=0.0, format="%.2f", key="in_weight")
            weight_uom = st.selectbox("Weight UOM 🔴", ["GSM (gram/sq meter)", "GPP (gram/piece)", "Oz (ounce/sq yard)"], key="in_wuom")

    # --- SECTION 4: COSTING & LOGISTICS ---
    st.markdown("### 4. Costing & Logistics")
    with st.container(border=True):
        # 1. Primary Inputs
        f1, f2, f3 = st.columns(3)
        with f1:
            cost = st.number_input("Original Cost 🔴", min_value=0.0, format="%.2f", key="in_cost")
        with f2:
            curr = st.selectbox("Currency 🔴", ["USD", "VND", "RMB", "EUR"], key="in_curr")
        with f3:
            sup_tolerance = st.number_input("Supplier Tolerance (%)", min_value=0.0, max_value=100.0, step=0.1, key="in_sup_tol")

        # --- LIVE CALCULATIONS (Part 1: Effective Cost) ---
        # Logic: Effective Cost = Original Cost + (Tolerance %)
        calc_effective_cost = 0.0
        if cost > 0:
            calc_effective_cost = cost + (cost * (sup_tolerance / 100.0))
            st.info(f"📊 **Effective Cost:** {calc_effective_cost:,.2f} {curr}")

        st.write("") 

        # 2. Advanced Dropdown
        with st.expander("Select for advanced cost calculation"):
            # VAT & Duty
            v1, v2 = st.columns([3, 1])
            with v1: vat = st.selectbox("Vietnam VAT Rate (%)", ["8%", "10%", "0%", "N/A"], key="in_vat")
            with v2: 
                st.write(""); st.write("")
                ref_vat = st.checkbox("Refundable VAT", key="in_ref_vat")

            d1, d2 = st.columns([3, 1])
            with d1: duty = st.number_input("Import Duty (%)", min_value=0.0, step=0.1, key="in_duty")
            with d2: 
                st.write(""); st.write("")
                ref_duty = st.checkbox("Refundable Import Duty", key="in_ref_duty")

            # Logistics Inputs
            l1, l2 = st.columns(2)
            with l1: ship_term = st.selectbox("Shipping Term", ["EXW", "FOB", "DDP", "CIF", "DAP"], key="in_ship_term")
            with l2: log_rate = st.number_input("Logistics Rate", min_value=0.0, step=0.1, help="Used for Landed Cost (%) and Logistics Fee (Weight * Rate)", key="in_log_rate")
            
            refundable = st.checkbox("Refundable Tolerance (General)", key="in_ref_tol")

            # --- LIVE CALCULATIONS (Part 2: Landed Cost & Fee) ---
            calc_landed_cost = 0.0
            calc_logistics_fee = 0.0
            
            if calc_effective_cost > 0:
                # A. Landed Cost Calculation: Effective Cost + (Logistics Rate %)
                # Formula: ((Logistics Rate / 100) * Effective Cost) + Effective Cost
                calc_landed_cost = ((log_rate / 100.0) * calc_effective_cost) + calc_effective_cost
                
                # B. Logistics Fee Calculation: Weight * Logistics Rate
                # Formula: weight_per_unit * logistics_rate
                w_val = weight if weight else 0.0
                calc_logistics_fee = w_val * (log_rate / 100.0)
                st.divider()
                st.markdown("#### Calculated Results")
                r1, r2 = st.columns(2)
                r1.metric("Landed Cost (Unit)", f"{calc_landed_cost:,.2f} {curr}", help="Effective Cost + Logistics Rate %")
                r2.metric("Logistics Fee", f"{calc_logistics_fee:,.2f}", help="Weight * Logistics Rate %")

    # --- BOTTOM ACTION BAR ---
    st.write(""); st.write("")
    action_col1, action_col2 = st.columns([1, 1])
    
    # --- INTERNAL HELPER ---
    def _get_payload():
        fabric_data = st.session_state.fabric_stack if st.session_state.fabric_stack else []

        payload = {
            # Standard Fields
            "material_name": name,
            "material_type": m_type,
            "supplier_name": supplier,
            "ref_id": ref_id,
            "country_of_origin": country,
            "unit_of_measurement": uom,
            "fabric_composition": fabric_data,
            "fabric_roll_width": width if width else None,
            "fabric_cut_width": cut_width if cut_width else None,
            "fabric_cut_width_no_shrinkage": cut_width_no_shrink if cut_width_no_shrink else None,
            "generic_material_size": gen_size,
            "weight_per_unit": weight if weight else None,
            "weight_uom": weight_uom,
            "weft_shrinkage": weft,
            "werp_shrinkage": werp,
            "original_cost_per_unit": cost if cost else None,
            "native_cost_currency": curr,
            
            # Input Fields
            "supplier_selling_tolerance": sup_tolerance,
            "refundable_tolerance": refundable,
            "vietnam_vat_rate": vat,
            "refundable_vat": ref_vat,
            "import_duty": duty,
            "refundable_import_duty": ref_duty,
            "shipping_term": ship_term,
            "logistics_rate": log_rate,
            
            # --- CALCULATED FIELDS (Stored to DB) ---
            "effective_cost_per_unit": calc_effective_cost if calc_effective_cost > 0 else None,
            "landed_cost_per_unit": calc_landed_cost if calc_landed_cost > 0 else None,
            "logistics_fee_per_unit": calc_logistics_fee if calc_logistics_fee > 0 else None
        }
        return {k: v for k, v in payload.items() if v is not None}

    # --- INTERNAL SUBMITTER ---
    def _submit(is_submit):
        data = _get_payload()
        endpoint = "/material_input/create_and_submit" if is_submit else "/material_input/create_draft"
        
        with st.spinner("Processing..."):
            res = get_api(endpoint, data)
        
        if res:
            st.success(f"Success! {res.get('message')}")
            st.session_state.fabric_stack = [] 
            time.sleep(1)
            st.session_state.view = 'list'
            st.rerun()
        else:
            st.error("Submission failed. Check API connection.")

    # --- BUTTONS ---
    if action_col1.button("💾 Save Draft", use_container_width=True):
        _submit(is_submit=False)

    if action_col2.button("🚀 Create & Submit", type="primary", use_container_width=True):
        if not name or not supplier:
            st.error("Missing required fields (🔴).")
        elif "Fabric" in m_type and current_total != 100:
            st.error(f"Fabric composition must be 100% (Current: {current_total}%)")
        else:
            _submit(is_submit=True)
# -----------------------------------------------------------------------------
# 7. VIEW: DETAIL
# -----------------------------------------------------------------------------
def view_detail():
    doc_id = st.session_state.selected_id
    c_back, c_title = st.columns([1, 5])
    with c_back:
        if st.button("← Back"):
            st.session_state.view = 'list'
            st.rerun()
    with c_title:
        st.title(f"🔎 Details: {doc_id}")
    
    data = get_api("/material_details/dashboard", {"document_id": doc_id})
    if not data:
        st.error("Could not load details.")
        return

    with st.container(border=True):
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Status", data.get('verification_status'))
        m2.metric("Supplier", data.get('supplier'))
        m3.metric("Type", data.get('material_type'))
        m4.metric("Cost", data.get('cost_display'))

    t1, t2, t3, t4, t5 = st.tabs(["Overview", "Technical Specs", "Cost Details", "History", "SKUs"])
    with t1: st.json(data)
    with t2:
        tech = get_api("/material_details/technical", {"document_id": doc_id})
        if tech: st.table(pd.DataFrame(tech.items(), columns=["Specification", "Value"]))
    with t3:
        cost = get_api("/material_details/cost", {"document_id": doc_id})
        if cost: st.dataframe(cost, use_container_width=True)
    with t4:
        hist = get_api("/material_details/history", {"document_id": doc_id})
        if hist: st.dataframe(hist, use_container_width=True)
    with t5:
        skus = get_api("/material_sku/get", {"document_id": doc_id})
        if skus:
            st.dataframe(pd.DataFrame(skus), use_container_width=True)
        else:
            st.info("No SKUs found.")

        st.divider()
        st.write("➕ **Add New Variant**")
        
        with st.form("sku_form"):
            c1, c2 = st.columns(2)
            ref = c1.text_input("Ref ID")
            qr = c2.text_input("QR Data")
            
            c3, c4, c5 = st.columns(3)
            col = c3.text_input("Color")
            siz = c4.text_input("Size")
            sco = c5.number_input("Cost Override", 0.0)
            
            submitted = st.form_submit_button("Add SKU")
            
            if submitted:
                payload = {
                    "document_id": doc_id,
                    "ref_id": ref,
                    "qr_data": qr,
                    "color": col,
                    "size": siz,
                    "sku_cost_override": sco
                }
                res = get_api("/material_sku/create", payload)
                if res:
                    st.success("SKU Created!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Failed to create SKU.")

render_sidebar()
if st.session_state.view == 'list': view_dashboard()
elif st.session_state.view == 'create': view_create()
elif st.session_state.view == 'detail': view_detail()