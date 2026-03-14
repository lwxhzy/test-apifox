from typing import Optional, List
from pydantic import BaseModel, Field


class ItemCreate(BaseModel):
    name: str = Field(..., description="物品名称", examples=["苹果"])
    price: float = Field(..., description="价格", ge=0, examples=[9.99])
    description: Optional[str] = Field(None, description="物品描述")


class ItemResponse(BaseModel):
    id: int = Field(..., description="物品 ID")
    name: str = Field(..., description="物品名称")
    price: float = Field(..., description="价格")
    description: Optional[str] = Field(None, description="物品描述")


class ItemListResponse(BaseModel):
    items: List[ItemResponse] = Field(..., description="物品列表")
    total: int = Field(..., description="总数量")
