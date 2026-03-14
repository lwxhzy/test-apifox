from fastapi import APIRouter, Query
from typing import Optional
from app.schemas import ItemCreate, ItemResponse, ItemListResponse

router = APIRouter(prefix="/api/v1", tags=["物品管理"])


@router.get(
    "/items",
    summary="获取物品列表",
    description="分页查询物品列表，支持按名称搜索",
    response_model=ItemListResponse,
)
async def list_items(
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    page: int = Query(1, description="页码", ge=1),
    page_size: int = Query(20, description="每页数量", ge=1, le=100),
):
    return {"items": [], "total": 0}


@router.post(
    "/items",
    summary="创建物品",
    description="创建一个新的物品",
    response_model=ItemResponse,
)
async def create_item(item: ItemCreate):
    return {"id": 1, **item.model_dump()}


@router.get(
    "/items/{item_id}",
    summary="获取物品详情",
    description="根据 ID 获取物品详细信息",
    response_model=ItemResponse,
)
async def get_item(item_id: int):
    return {"id": item_id, "name": "示例", "price": 9.99, "description": None}
