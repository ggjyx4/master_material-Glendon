import anvil.server
from pydantic import BaseModel, Field
from typing import List, Optional

class SkuRequest(BaseModel):
    """Request to fetch SKUs for a specific material"""
    document_id: str = Field(..., description="The Master Material ID (e.g., MAT-001)")

class CreateSkuRequest(BaseModel):
    """Request to create a new SKU"""
    document_id: str = Field(..., description="The Master Material ID to link this SKU to")
    ref_id: str = Field(..., description="External Reference ID")
    qr_data: str = Field(..., description="QR Code content")
    sku_cost_override: float = Field(0.0, description="Cost override for this specific SKU")
    color: Optional[str] = Field(None, description="Color variant")
    size: Optional[str] = Field(None, description="Size variant")

class SkuResponse(BaseModel):
    """Response model for a single SKU"""
    id: str
    ref_id: str
    qr_data: str
    sku_cost_override: float
    color: Optional[str] = None
    size: Optional[str] = None