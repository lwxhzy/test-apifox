from fastapi import APIRouter, Query, Path, Body
from typing import Optional, List

from app.schemas import (
    MessageResponse,
    # 用户
    UserCreate, UserUpdate, UserResponse, UserListResponse,
    LoginRequest, LoginResponse, UserRole,
    # 分类
    CategoryCreate, CategoryResponse, CategoryTreeNode,
    # 物品
    ItemCreate, ItemUpdate, ItemResponse, ItemListResponse, ItemStatus,
    # 订单
    OrderCreate, OrderResponse, OrderListResponse, OrderStatus,
    # 统计
    DashboardResponse,
)

router = APIRouter(prefix="/api/v1")


# ──────────────────────────────────────────────
# 认证
# ──────────────────────────────────────────────

auth_router = APIRouter(prefix="/auth", tags=["认证"])


@auth_router.post(
    "/login",
    summary="用户登录",
    description="使用用户名和密码登录，返回 JWT 令牌",
    response_model=LoginResponse,
)
async def login(body: LoginRequest):
    return {
        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "token_type": "bearer",
        "expires_in": 3600,
    }


@auth_router.post(
    "/logout",
    summary="用户登出",
    description="注销当前用户的访问令牌",
    response_model=MessageResponse,
)
async def logout():
    return {"message": "登出成功"}


# ──────────────────────────────────────────────
# 用户管理
# ──────────────────────────────────────────────

user_router = APIRouter(prefix="/users", tags=["用户管理"])


@user_router.get(
    "",
    summary="获取用户列表",
    description="分页查询用户列表，支持按用户名或邮箱搜索，支持按角色筛选",
    response_model=UserListResponse,
)
async def list_users(
    keyword: Optional[str] = Query(None, description="搜索关键词，匹配用户名或邮箱"),
    role: Optional[UserRole] = Query(None, description="按角色筛选"),
    is_active: Optional[bool] = Query(None, description="按启用状态筛选"),
    page: int = Query(1, description="页码", ge=1),
    page_size: int = Query(20, description="每页数量", ge=1, le=100),
):
    return {"users": [], "total": 0}


@user_router.post(
    "",
    summary="创建用户",
    description="注册一个新用户，用户名和邮箱不可重复",
    response_model=UserResponse,
    status_code=201,
)
async def create_user(body: UserCreate):
    return {
        "id": 1, "username": body.username, "email": body.email,
        "role": body.role, "nickname": body.nickname,
        "is_active": True, "created_at": "2024-01-01T00:00:00Z",
    }


@user_router.get(
    "/{user_id}",
    summary="获取用户详情",
    description="根据用户 ID 获取用户详细信息",
    response_model=UserResponse,
)
async def get_user(
    user_id: int = Path(..., description="用户 ID", examples=[1]),
):
    return {
        "id": user_id, "username": "zhangsan", "email": "zhangsan@example.com",
        "role": "viewer", "nickname": "张三",
        "is_active": True, "created_at": "2024-01-01T00:00:00Z",
    }


@user_router.put(
    "/{user_id}",
    summary="更新用户信息",
    description="更新指定用户的基本信息，仅传入需要修改的字段",
    response_model=UserResponse,
)
async def update_user(
    user_id: int = Path(..., description="用户 ID"),
    body: UserUpdate = Body(...),
):
    return {
        "id": user_id, "username": "zhangsan", "email": "zhangsan@example.com",
        "role": "viewer", "nickname": "张三",
        "is_active": True, "created_at": "2024-01-01T00:00:00Z",
    }


@user_router.delete(
    "/{user_id}",
    summary="删除用户",
    description="软删除指定用户，将 is_active 置为 false",
    response_model=MessageResponse,
)
async def delete_user(
    user_id: int = Path(..., description="用户 ID"),
):
    return {"message": "用户已删除"}


# ──────────────────────────────────────────────
# 分类管理
# ──────────────────────────────────────────────

category_router = APIRouter(prefix="/categories", tags=["分类管理"])


@category_router.get(
    "",
    summary="获取分类列表",
    description="获取所有分类的扁平列表",
    response_model=List[CategoryResponse],
)
async def list_categories():
    return []


@category_router.get(
    "/tree",
    summary="获取分类树",
    description="以树形结构返回所有分类，包含层级关系",
    response_model=List[CategoryTreeNode],
)
async def get_category_tree():
    return []


@category_router.post(
    "",
    summary="创建分类",
    description="创建一个新的分类，可指定父分类实现多级分类",
    response_model=CategoryResponse,
    status_code=201,
)
async def create_category(body: CategoryCreate):
    return {
        "id": 1, "name": body.name, "parent_id": body.parent_id,
        "sort_order": body.sort_order, "icon": body.icon, "item_count": 0,
    }


@category_router.put(
    "/{category_id}",
    summary="更新分类",
    description="更新指定分类的名称、排序等信息",
    response_model=CategoryResponse,
)
async def update_category(
    category_id: int = Path(..., description="分类 ID"),
    body: CategoryCreate = Body(...),
):
    return {
        "id": category_id, "name": body.name, "parent_id": body.parent_id,
        "sort_order": body.sort_order, "icon": body.icon, "item_count": 0,
    }


@category_router.delete(
    "/{category_id}",
    summary="删除分类",
    description="删除指定分类。如果分类下有物品，需要先移除或转移物品",
    response_model=MessageResponse,
)
async def delete_category(
    category_id: int = Path(..., description="分类 ID"),
):
    return {"message": "分类已删除"}


# ──────────────────────────────────────────────
# 物品管理
# ──────────────────────────────────────────────

item_router = APIRouter(prefix="/items", tags=["物品管理"])


@item_router.get(
    "",
    summary="获取物品列表",
    description="分页查询物品列表，支持按名称搜索、按分类和状态筛选、按价格排序",
    response_model=ItemListResponse,
)
async def list_items(
    keyword: Optional[str] = Query(None, description="搜索关键词，模糊匹配物品名称"),
    category_id: Optional[int] = Query(None, description="按分类 ID 筛选"),
    status: Optional[ItemStatus] = Query(None, description="按状态筛选"),
    min_price: Optional[float] = Query(None, description="最低价格", ge=0),
    max_price: Optional[float] = Query(None, description="最高价格", ge=0),
    sort_by: Optional[str] = Query(
        "created_at", description="排序字段：price / created_at / stock",
    ),
    sort_order: Optional[str] = Query(
        "desc", description="排序方向：asc / desc",
    ),
    page: int = Query(1, description="页码", ge=1),
    page_size: int = Query(20, description="每页数量", ge=1, le=100),
):
    return {"items": [], "total": 0}


@item_router.post(
    "",
    summary="创建物品",
    description="创建一个新的物品，初始状态为 draft",
    response_model=ItemResponse,
    status_code=201,
)
async def create_item(body: ItemCreate):
    return {
        "id": 1, **body.model_dump(),
        "category_name": "水果",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z",
    }


@item_router.get(
    "/{item_id}",
    summary="获取物品详情",
    description="根据 ID 获取物品详细信息，包含分类名称",
    response_model=ItemResponse,
)
async def get_item(
    item_id: int = Path(..., description="物品 ID", examples=[1]),
):
    return {
        "id": item_id, "name": "苹果", "price": 9.99,
        "description": "新鲜红富士", "category_id": 1, "category_name": "水果",
        "stock": 100, "status": "active", "tags": ["新品", "热卖"],
        "images": ["https://cdn.example.com/img/apple.jpg"],
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z",
    }


@item_router.put(
    "/{item_id}",
    summary="更新物品",
    description="更新指定物品的信息，仅传入需要修改的字段",
    response_model=ItemResponse,
)
async def update_item(
    item_id: int = Path(..., description="物品 ID"),
    body: ItemUpdate = Body(...),
):
    return {
        "id": item_id, "name": "苹果", "price": 9.99,
        "description": None, "category_id": 1, "category_name": "水果",
        "stock": 100, "status": "active", "tags": [], "images": [],
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-02T00:00:00Z",
    }


@item_router.delete(
    "/{item_id}",
    summary="删除物品",
    description="永久删除指定物品，删除后不可恢复",
    response_model=MessageResponse,
)
async def delete_item(
    item_id: int = Path(..., description="物品 ID"),
):
    return {"message": "物品已删除"}


@item_router.patch(
    "/{item_id}/status",
    summary="更新物品状态",
    description="单独更新物品状态，如上架 (active)、下架 (archived)、售罄 (sold_out)",
    response_model=ItemResponse,
)
async def update_item_status(
    item_id: int = Path(..., description="物品 ID"),
    status: ItemStatus = Body(..., embed=True, description="目标状态"),
):
    return {
        "id": item_id, "name": "苹果", "price": 9.99,
        "description": None, "category_id": 1, "category_name": "水果",
        "stock": 100, "status": status, "tags": [], "images": [],
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-02T00:00:00Z",
    }


# ──────────────────────────────────────────────
# 订单管理
# ──────────────────────────────────────────────

order_router = APIRouter(prefix="/orders", tags=["订单管理"])


@order_router.get(
    "",
    summary="获取订单列表",
    description="分页查询订单列表，支持按状态筛选和时间范围查询",
    response_model=OrderListResponse,
)
async def list_orders(
    status: Optional[OrderStatus] = Query(None, description="按订单状态筛选"),
    user_id: Optional[int] = Query(None, description="按用户 ID 筛选"),
    start_date: Optional[str] = Query(None, description="起始日期，格式 YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="截止日期，格式 YYYY-MM-DD"),
    page: int = Query(1, description="页码", ge=1),
    page_size: int = Query(20, description="每页数量", ge=1, le=100),
):
    return {"orders": [], "total": 0}


@order_router.post(
    "",
    summary="创建订单",
    description="创建新订单，自动计算商品金额。库存不足时返回 400 错误",
    response_model=OrderResponse,
    status_code=201,
)
async def create_order(body: OrderCreate):
    return {
        "id": 1001, "order_no": "ORD20240101001", "user_id": 1,
        "status": "pending",
        "items": [
            {"item_id": 1, "item_name": "苹果", "price": 9.99, "quantity": 2, "subtotal": 19.98},
        ],
        "total_amount": 19.98,
        "shipping_address": body.shipping_address,
        "receiver_name": body.receiver_name,
        "receiver_phone": body.receiver_phone,
        "remark": body.remark,
        "created_at": "2024-01-01T10:30:00Z",
        "paid_at": None, "shipped_at": None,
    }


@order_router.get(
    "/{order_id}",
    summary="获取订单详情",
    description="根据订单 ID 获取完整订单信息，包含商品明细",
    response_model=OrderResponse,
)
async def get_order(
    order_id: int = Path(..., description="订单 ID", examples=[1001]),
):
    return {
        "id": order_id, "order_no": "ORD20240101001", "user_id": 1,
        "status": "pending", "items": [],
        "total_amount": 19.98,
        "shipping_address": "北京市朝阳区望京 SOHO",
        "receiver_name": "张三", "receiver_phone": "13800138000",
        "remark": None,
        "created_at": "2024-01-01T10:30:00Z",
        "paid_at": None, "shipped_at": None,
    }


@order_router.patch(
    "/{order_id}/pay",
    summary="订单支付",
    description="将待支付订单标记为已支付",
    response_model=OrderResponse,
)
async def pay_order(
    order_id: int = Path(..., description="订单 ID"),
):
    return {
        "id": order_id, "order_no": "ORD20240101001", "user_id": 1,
        "status": "paid", "items": [],
        "total_amount": 19.98,
        "shipping_address": "北京市朝阳区望京 SOHO",
        "receiver_name": "张三", "receiver_phone": "13800138000",
        "remark": None,
        "created_at": "2024-01-01T10:30:00Z",
        "paid_at": "2024-01-01T10:35:00Z", "shipped_at": None,
    }


@order_router.patch(
    "/{order_id}/ship",
    summary="订单发货",
    description="将已支付订单标记为已发货，需要管理员权限",
    response_model=OrderResponse,
)
async def ship_order(
    order_id: int = Path(..., description="订单 ID"),
):
    return {
        "id": order_id, "order_no": "ORD20240101001", "user_id": 1,
        "status": "shipped", "items": [],
        "total_amount": 19.98,
        "shipping_address": "北京市朝阳区望京 SOHO",
        "receiver_name": "张三", "receiver_phone": "13800138000",
        "remark": None,
        "created_at": "2024-01-01T10:30:00Z",
        "paid_at": "2024-01-01T10:35:00Z",
        "shipped_at": "2024-01-02T09:00:00Z",
    }


@order_router.patch(
    "/{order_id}/cancel",
    summary="取消订单",
    description="取消订单。仅待支付状态的订单可取消，已支付订单请走退款流程",
    response_model=OrderResponse,
)
async def cancel_order(
    order_id: int = Path(..., description="订单 ID"),
):
    return {
        "id": order_id, "order_no": "ORD20240101001", "user_id": 1,
        "status": "cancelled", "items": [],
        "total_amount": 19.98,
        "shipping_address": "北京市朝阳区望京 SOHO",
        "receiver_name": "张三", "receiver_phone": "13800138000",
        "remark": None,
        "created_at": "2024-01-01T10:30:00Z",
        "paid_at": None, "shipped_at": None,
    }


# ──────────────────────────────────────────────
# 数据统计
# ──────────────────────────────────────────────

stats_router = APIRouter(prefix="/stats", tags=["数据统计"])


@stats_router.get(
    "/dashboard",
    summary="获取仪表盘数据",
    description="获取系统总览数据，包括用户数、物品数、订单数、营收及最近 7 天趋势",
    response_model=DashboardResponse,
)
async def get_dashboard():
    return {
        "total_users": 1024,
        "total_items": 256,
        "total_orders": 8192,
        "total_revenue": 1256800.00,
        "recent_stats": [
            {"date": "2024-01-07", "order_count": 42, "revenue": 12580.50, "new_users": 15},
            {"date": "2024-01-06", "order_count": 38, "revenue": 10200.00, "new_users": 12},
        ],
    }


# ── 注册所有子路由 ──

router.include_router(auth_router)
router.include_router(user_router)
router.include_router(category_router)
router.include_router(item_router)
router.include_router(order_router)
router.include_router(stats_router)
