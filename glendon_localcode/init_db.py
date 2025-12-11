import os
import psycopg2

# Get the secret password from Docker
DB_URL = os.environ.get("DATABASE_URL")

# --- 1. Master Table (The Folder) ---
CREATE_MASTER = """
CREATE TABLE IF NOT EXISTS master_materials (
    document_id TEXT PRIMARY KEY,
    current_version INT,
    current_version_uid TEXT,
    
    -- HISTORY ARRAYS (Denormalized Data)
    version_history JSONB DEFAULT '[]',      -- List of full version objects
    version_history_uid JSONB DEFAULT '[]',  -- List of version UUIDs strings

    -- Meta data (Folder Level)
    created_at TIMESTAMP,
    created_by TEXT, -- Storing User as TEXT (ID or JSON)
    submitted_at TIMESTAMP,
    submitted_by TEXT,
    last_verified_date TIMESTAMP,
    last_verified_by TEXT
);
"""

# --- 2. Version Table (The Data) ---
CREATE_VERSION = """
CREATE TABLE IF NOT EXISTS material_versions (
    -- Identification
    document_uid TEXT PRIMARY KEY,
    document_id TEXT REFERENCES master_materials(document_id), -- The link to the Master Folder
    ver_num INT,
    change_description TEXT,
    
    -- Meta Data
    created_at TIMESTAMP,
    created_by TEXT,
    submitted_at TIMESTAMP,
    submitted_by TEXT,
    last_verified_date TIMESTAMP,
    last_verified_by TEXT,
    
    -- Material IDs
    ref_id TEXT,               -- id from supplier
    master_material_id TEXT,   -- human-readable id (vin_mmat_...)
    status TEXT,
    
    -- Supplier Info
    supplier JSONB,            -- Storing the Supplier object as JSON
    supplier_name TEXT,
    country_of_origin TEXT,
    estimated_logistics_lead_time INT,
    
    -- Core Material Info
    material_name TEXT,
    material_type TEXT,        -- Enum stored as text
    qr_id TEXT,
    hanger_pdf_id TEXT,
    picture_id TEXT,

    -- Technical Specifications
    unit_of_measurement TEXT,
    fabric_composition JSONB,  -- list[tuple[float, Material_composition]]
    generic_material_composition TEXT,
    fabric_roll_width REAL,
    fabric_cut_width REAL,
    fabric_cut_width_no_shrinkage REAL,
    weight_per_unit REAL,
    weight_uom TEXT,
    generic_material_size TEXT,
    weft_shrinkage REAL,
    werp_shrinkage REAL,

    -- Cost (Basic)
    original_cost_per_unit REAL,
    native_cost_currency TEXT,
    supplier_selling_tolerance REAL,
    refundable_tolerance BOOLEAN,
    effective_cost_per_unit REAL,

    -- Cost (Advanced)
    vietnam_vat_rate TEXT,
    refundable_vat BOOLEAN,
    import_duty REAL,
    refundable_import_duty BOOLEAN,
    shipping_term TEXT,
    logistics_rate REAL,
    logistics_fee_per_unit REAL,
    landed_cost_per_unit REAL,

    -- Constraint: Ensure version uniqueness per master document
    UNIQUE (document_id, ver_num)
);
"""

# --- 3. SKU Table (The Variants) ---
CREATE_SKU = """
CREATE TABLE IF NOT EXISTS material_skus (
    id TEXT PRIMARY KEY,
    
    -- Link to Master Material
    master_material_document_id TEXT REFERENCES master_materials(document_id), 
    
    ref_id TEXT,
    color TEXT,
    size TEXT,
    qr_data TEXT,
    sku_cost_override REAL
);
"""

def init_db():
    if not DB_URL:
        print("❌ Error: DATABASE_URL is missing. Run this inside Docker!")
        return
    
    try:
        conn = psycopg2.connect(DB_URL)
        cur = conn.cursor()
        print("🔨 Building new tables (Master, Version, SKU)...")
        
        # Execute creation scripts
        cur.execute(CREATE_MASTER)
        cur.execute(CREATE_VERSION)
        cur.execute(CREATE_SKU)
        
        conn.commit()
        cur.close()
        conn.close()
        print("✅ Success! Tables created matching the Pydantic models.")
    except Exception as e:
        print(f"❌ Failed to create tables: {e}")

if __name__ == "__main__":
    init_db()