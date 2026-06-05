from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    username: Optional[str] = None
    user_id: Optional[int] = None


class UserLogin(BaseModel):
    username: str
    password: str


class UserBase(BaseModel):
    username: str
    full_name: Optional[str] = None
    store_id: Optional[int] = None
    is_admin: bool = False


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class StoreBase(BaseModel):
    name: str
    address: Optional[str] = None
    phone: Optional[str] = None


class StoreCreate(StoreBase):
    pass


class StoreResponse(StoreBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class MaterialCategoryBase(BaseModel):
    name: str
    description: Optional[str] = None


class MaterialCategoryCreate(MaterialCategoryBase):
    pass


class MaterialCategoryResponse(MaterialCategoryBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class MaterialBase(BaseModel):
    code: str
    name: str
    specification: Optional[str] = None
    category_id: Optional[int] = None
    store_id: Optional[int] = None
    shelf_life_days: int = 7


class MaterialCreate(MaterialBase):
    pass


class MaterialUpdate(BaseModel):
    name: Optional[str] = None
    specification: Optional[str] = None
    category_id: Optional[int] = None
    store_id: Optional[int] = None
    shelf_life_days: Optional[int] = None


class MaterialResponse(MaterialBase):
    id: int
    stock_quantity: float
    open_status: bool
    open_date: Optional[date] = None
    expiry_date: Optional[date] = None
    current_status: str
    created_at: datetime
    category: Optional[MaterialCategoryResponse] = None

    class Config:
        from_attributes = True


class StockInBase(BaseModel):
    material_id: int
    quantity: float = Field(gt=0)
    batch_number: Optional[str] = None
    supplier: Optional[str] = None
    purchase_date: Optional[date] = None
    expiry_date: Optional[date] = None
    remark: Optional[str] = None


class StockInCreate(StockInBase):
    pass


class StockInResponse(StockInBase):
    id: int
    operator_id: Optional[int] = None
    created_at: datetime
    material: Optional[MaterialResponse] = None

    class Config:
        from_attributes = True


class OpenRecordBase(BaseModel):
    material_id: int
    open_date: date
    expiry_date: date
    remark: Optional[str] = None

    @field_validator('expiry_date')
    def expiry_not_before_open(cls, v, values):
        if 'open_date' in values.data and v < values.data['open_date']:
            raise ValueError('失效日期不能早于开封日期')
        return v


class OpenRecordCreate(OpenRecordBase):
    pass


class OpenRecordResponse(OpenRecordBase):
    id: int
    operator_id: Optional[int] = None
    created_at: datetime
    material: Optional[MaterialResponse] = None

    class Config:
        from_attributes = True


class DamageRecordBase(BaseModel):
    material_id: int
    quantity: float = Field(gt=0)
    damage_date: Optional[date] = None
    reason: str
    remark: Optional[str] = None


class DamageRecordCreate(DamageRecordBase):
    pass


class DamageRecordResponse(DamageRecordBase):
    id: int
    operator_id: Optional[int] = None
    created_at: datetime
    material: Optional[MaterialResponse] = None

    class Config:
        from_attributes = True


class ExpiryWarningResponse(BaseModel):
    id: int
    code: str
    name: str
    expiry_date: date
    days_remaining: int
    current_status: str


class DamageRankingResponse(BaseModel):
    material_id: int
    material_name: str
    material_code: str
    total_damage: float
    damage_count: int


class CategoryStockResponse(BaseModel):
    category_id: int
    category_name: str
    total_stock: float
    material_count: int


class DashboardStats(BaseModel):
    expiring_soon_count: int
    expired_count: int
    total_materials: int
    total_stock: float
    damage_ranking: List[DamageRankingResponse]
    category_stock: List[CategoryStockResponse]
