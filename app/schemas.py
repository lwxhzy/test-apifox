from typing import Optional, List
from enum import Enum
from pydantic import BaseModel, Field


# ──────────────────────────────────────────────
# 通用
# ──────────────────────────────────────────────

class MessageResponse(BaseModel):
    message: str = Field(..., description="提示信息", examples=["操作成功"])


class ErrorResponse(BaseModel):
    detail: str = Field(..., description="错误信息", examples=["资源不存在"])


class ValidationErrorItem(BaseModel):
    field: str = Field(..., description="出错字段", examples=["price"])
    message: str = Field(..., description="错误描述", examples=["值必须大于 0"])


class ValidationErrorResponse(BaseModel):
    detail: List[ValidationErrorItem] = Field(..., description="校验错误列表")


# ──────────────────────────────────────────────
# 用户模块
# ──────────────────────────────────────────────

class UserRole(str, Enum):
    admin = "admin"
    editor = "editor"
    viewer = "viewer"


class UserCreate(BaseModel):
    username: str = Field(
        ..., description="用户名，3-20 个字符", min_length=3, max_length=20,
        examples=["zhangsan"],
    )
    email: str = Field(
        ..., description="邮箱地址", examples=["zhangsan@example.com"],
    )
    password: str = Field(
        ..., description="密码，至少 8 位", min_length=8,
        examples=["P@ssw0rd123"],
    )
    role: UserRole = Field(
        UserRole.viewer, description="角色：admin / editor / viewer",
    )
    nickname: Optional[str] = Field(
        None, description="昵称", max_length=50, examples=["张三"],
    )


class UserUpdate(BaseModel):
    nickname: Optional[str] = Field(None, description="昵称", max_length=50)
    email: Optional[str] = Field(None, description="邮箱地址")
    role: Optional[UserRole] = Field(None, description="角色")


class UserResponse(BaseModel):
    id: int = Field(..., description="用户 ID", examples=[1])
    username: str = Field(..., description="用户名")
    email: str = Field(..., description="邮箱地址")
    role: UserRole = Field(..., description="角色")
    nickname: Optional[str] = Field(None, description="昵称")
    is_active: bool = Field(..., description="是否启用", examples=[True])
    created_at: str = Field(..., description="创建时间", examples=["2024-01-01T00:00:00Z"])


class UserListResponse(BaseModel):
    users: List[UserResponse] = Field(..., description="用户列表")
    total: int = Field(..., description="总数量")


class LoginRequest(BaseModel):
    username: str = Field(..., description="用户名", examples=["zhangsan"])
    password: str = Field(..., description="密码", examples=["P@ssw0rd123"])


class LoginResponse(BaseModel):
    access_token: str = Field(..., description="JWT 访问令牌")
    token_type: str = Field("bearer", description="令牌类型")
    expires_in: int = Field(..., description="过期时间（秒）", examples=[3600])


# ──────────────────────────────────────────────
# 分类模块
# ──────────────────────────────────────────────

class CategoryCreate(BaseModel):
    name: str = Field(
        ..., description="分类名称", max_length=30, examples=["水果"],
    )
    parent_id: Optional[int] = Field(
        None, description="父分类 ID，为空表示顶级分类",
    )
    sort_order: int = Field(
        0, description="排序权重，数值越小越靠前", ge=0, examples=[0],
    )
    icon: Optional[str] = Field(
        None, description="分类图标 URL",
        examples=["https://cdn.example.com/icons/fruit.png"],
    )


class CategoryResponse(BaseModel):
    id: int = Field(..., description="分类 ID", examples=[1])
    name: str = Field(..., description="分类名称")
    parent_id: Optional[int] = Field(None, description="父分类 ID")
    sort_order: int = Field(..., description="排序权重")
    icon: Optional[str] = Field(None, description="分类图标 URL")
    item_count: int = Field(..., description="该分类下物品数量", examples=[12])


class CategoryTreeNode(BaseModel):
    id: int = Field(..., description="分类 ID")
    name: str = Field(..., description="分类名称")
    icon: Optional[str] = Field(None, description="分类图标 URL")
    children: List["CategoryTreeNode"] = Field(
        default_factory=list, description="子分类列表",
    )


# ──────────────────────────────────────────────
# 物品模块（扩展）
# ──────────────────────────────────────────────

class ItemStatus(str, Enum):
    draft = "draft"
    active = "active"
    sold_out = "sold_out"
    archived = "archived"


class ItemCreate(BaseModel):
    name: str = Field(
        ..., description="物品名称，不超过 100 个字符",
        max_length=100, examples=["苹果"],
    )
    price: float = Field(
        ..., description="价格，单位：元", ge=0, examples=[9.99],
    )
    description: Optional[str] = Field(
        None, description="物品描述，支持 Markdown 格式", max_length=2000,
    )
    category_id: Optional[int] = Field(
        None, description="所属分类 ID", examples=[1],
    )
    stock: int = Field(
        0, description="库存数量", ge=0, examples=[100],
    )
    status: ItemStatus = Field(
        ItemStatus.draft, description="物品状态：draft / active / sold_out / archived",
    )
    tags: List[str] = Field(
        default_factory=list,
        description="物品标签列表", examples=[["新品", "热卖"]],
    )
    images: List[str] = Field(
        default_factory=list,
        description="物品图片 URL 列表",
        examples=[["https://cdn.example.com/img/apple.jpg"]],
    )


class ItemUpdate(BaseModel):
    name: Optional[str] = Field(None, description="物品名称", max_length=100)
    price: Optional[float] = Field(None, description="价格", ge=0)
    description: Optional[str] = Field(None, description="物品描述", max_length=2000)
    category_id: Optional[int] = Field(None, description="所属分类 ID")
    stock: Optional[int] = Field(None, description="库存数量", ge=0)
    status: Optional[ItemStatus] = Field(None, description="物品状态")
    tags: Optional[List[str]] = Field(None, description="物品标签列表")
    images: Optional[List[str]] = Field(None, description="物品图片 URL 列表")


class ItemResponse(BaseModel):
    id: int = Field(..., description="物品 ID", examples=[1])
    name: str = Field(..., description="物品名称")
    price: float = Field(..., description="价格")
    description: Optional[str] = Field(None, description="物品描述")
    category_id: Optional[int] = Field(None, description="所属分类 ID")
    category_name: Optional[str] = Field(None, description="分类名称", examples=["水果"])
    stock: int = Field(..., description="库存数量")
    status: ItemStatus = Field(..., description="物品状态")
    tags: List[str] = Field(default_factory=list, description="物品标签")
    images: List[str] = Field(default_factory=list, description="物品图片 URL 列表")
    created_at: str = Field(..., description="创建时间", examples=["2024-01-01T00:00:00Z"])
    updated_at: str = Field(..., description="更新时间", examples=["2024-01-01T00:00:00Z"])


class ItemListResponse(BaseModel):
    items: List[ItemResponse] = Field(..., description="物品列表")
    total: int = Field(..., description="总数量")


# ──────────────────────────────────────────────
# 订单模块
# ──────────────────────────────────────────────

class OrderStatus(str, Enum):
    pending = "pending"
    paid = "paid"
    shipped = "shipped"
    delivered = "delivered"
    cancelled = "cancelled"
    refunded = "refunded"


class OrderItemCreate(BaseModel):
    item_id: int = Field(..., description="物品 ID", examples=[1])
    quantity: int = Field(..., description="购买数量", ge=1, examples=[2])


class OrderItemResponse(BaseModel):
    item_id: int = Field(..., description="物品 ID")
    item_name: str = Field(..., description="物品名称", examples=["苹果"])
    price: float = Field(..., description="下单时单价", examples=[9.99])
    quantity: int = Field(..., description="购买数量")
    subtotal: float = Field(..., description="小计金额", examples=[19.98])


class OrderCreate(BaseModel):
    items: List[OrderItemCreate] = Field(
        ..., description="订单商品列表，至少一项", min_length=1,
    )
    shipping_address: str = Field(
        ..., description="收货地址", max_length=200,
        examples=["北京市朝阳区望京 SOHO T1 1001"],
    )
    receiver_name: str = Field(
        ..., description="收货人姓名", examples=["张三"],
    )
    receiver_phone: str = Field(
        ..., description="收货人手机号", examples=["13800138000"],
    )
    remark: Optional[str] = Field(
        None, description="订单备注", max_length=500,
    )


class OrderResponse(BaseModel):
    id: int = Field(..., description="订单 ID", examples=[1001])
    order_no: str = Field(..., description="订单编号", examples=["ORD20240101001"])
    user_id: int = Field(..., description="下单用户 ID")
    status: OrderStatus = Field(..., description="订单状态")
    items: List[OrderItemResponse] = Field(..., description="订单商品列表")
    total_amount: float = Field(..., description="订单总金额", examples=[59.97])
    shipping_address: str = Field(..., description="收货地址")
    receiver_name: str = Field(..., description="收货人姓名")
    receiver_phone: str = Field(..., description="收货人手机号")
    remark: Optional[str] = Field(None, description="订单备注")
    created_at: str = Field(..., description="下单时间", examples=["2024-01-01T10:30:00Z"])
    paid_at: Optional[str] = Field(None, description="支付时间")
    shipped_at: Optional[str] = Field(None, description="发货时间")


class OrderListResponse(BaseModel):
    orders: List[OrderResponse] = Field(..., description="订单列表")
    total: int = Field(..., description="总数量")


# ──────────────────────────────────────────────
# 统计模块
# ──────────────────────────────────────────────

class DailyStat(BaseModel):
    date: str = Field(..., description="日期", examples=["2024-01-01"])
    order_count: int = Field(..., description="订单数", examples=[42])
    revenue: float = Field(..., description="营收金额", examples=[12580.50])
    new_users: int = Field(..., description="新增用户数", examples=[15])


class DashboardResponse(BaseModel):
    total_users: int = Field(..., description="用户总数", examples=[1024])
    total_items: int = Field(..., description="物品总数", examples=[256])
    total_orders: int = Field(..., description="订单总数", examples=[8192])
    total_revenue: float = Field(..., description="累计营收", examples=[1256800.00])
    recent_stats: List[DailyStat] = Field(..., description="最近 7 天统计")
