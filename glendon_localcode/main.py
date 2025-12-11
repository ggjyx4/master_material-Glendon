from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import all your new controllers
from controller import (
    material_card_controller, 
    material_detail_controller, 
    material_input_controller,
    material_sku_input_controller 
)

# 1. Initialize the App
app = FastAPI(
    title="Material Master API",
    description="API for Material Management (Glendon)",
    version="1.0.0"
)

# 2. Add CORS (Important if your frontend is on a different domain/port)
# This allows your Streamlit app or React app to talk to this API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. Include Routers
app.include_router(material_card_controller.router)
app.include_router(material_detail_controller.router)
app.include_router(material_input_controller.router)
app.include_router(material_sku_input_controller.router)

# 4. Root endpoint (Health check)
@app.get("/")
def root():
    return {"status": "System is running", "docs_url": "/docs"}