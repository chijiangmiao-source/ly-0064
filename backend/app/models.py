from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey, Boolean, UniqueConstraint
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100))
    store_id = Column(Integer, ForeignKey("stores.id"))
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    store = relationship("Store", back_populates="users")


class Store(Base):
    __tablename__ = "stores"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    address = Column(String(255))
    phone = Column(String(20))
    created_at = Column(DateTime, default=datetime.utcnow)

    users = relationship("User", back_populates="store")
    materials = relationship("Material", back_populates="store")


class MaterialCategory(Base):
    __tablename__ = "material_categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False, unique=True)
    description = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)

    materials = relationship("Material", back_populates="category")


class Material(Base):
    __tablename__ = "materials"
    __table_args__ = (
        UniqueConstraint('code', 'store_id', 'batch_number', name='uq_material_code_store_batch'),
    )

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    specification = Column(String(100))
    category_id = Column(Integer, ForeignKey("material_categories.id"))
    store_id = Column(Integer, ForeignKey("stores.id"))
    stock_quantity = Column(Float, default=0)
    open_status = Column(Boolean, default=False)
    open_date = Column(Date)
    expiry_date = Column(Date)
    shelf_life_days = Column(Integer, default=7)
    batch_number = Column(String(100), default='')
    created_at = Column(DateTime, default=datetime.utcnow)

    category = relationship("MaterialCategory", back_populates="materials")
    store = relationship("Store", back_populates="materials")
    stock_ins = relationship("StockIn", back_populates="material")
    open_records = relationship("OpenRecord", back_populates="material")
    damage_records = relationship("DamageRecord", back_populates="material")
    usage_records = relationship("UsageRecord", back_populates="material")

    @property
    def current_status(self):
        today = date.today()
        if self.expiry_date and today > self.expiry_date:
            return "expired"
        if self.open_status:
            return "opened"
        if self.stock_quantity > 0:
            return "in_stock"
        return "out_of_stock"


class StockIn(Base):
    __tablename__ = "stock_ins"

    id = Column(Integer, primary_key=True, index=True)
    material_id = Column(Integer, ForeignKey("materials.id"), nullable=False)
    quantity = Column(Float, nullable=False)
    batch_number = Column(String(100))
    supplier = Column(String(100))
    purchase_date = Column(Date, default=date.today)
    expiry_date = Column(Date)
    operator_id = Column(Integer, ForeignKey("users.id"))
    remark = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)

    material = relationship("Material", back_populates="stock_ins")


class OpenRecord(Base):
    __tablename__ = "open_records"

    id = Column(Integer, primary_key=True, index=True)
    material_id = Column(Integer, ForeignKey("materials.id"), nullable=False)
    open_date = Column(Date, nullable=False)
    expiry_date = Column(Date, nullable=False)
    operator_id = Column(Integer, ForeignKey("users.id"))
    remark = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)

    material = relationship("Material", back_populates="open_records")


class DamageRecord(Base):
    __tablename__ = "damage_records"

    id = Column(Integer, primary_key=True, index=True)
    material_id = Column(Integer, ForeignKey("materials.id"), nullable=False)
    quantity = Column(Float, nullable=False)
    damage_date = Column(Date, default=date.today)
    reason = Column(String(255), nullable=False)
    operator_id = Column(Integer, ForeignKey("users.id"))
    remark = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)

    material = relationship("Material", back_populates="damage_records")


class UsageRecord(Base):
    __tablename__ = "usage_records"

    id = Column(Integer, primary_key=True, index=True)
    material_id = Column(Integer, ForeignKey("materials.id"), nullable=False)
    store_id = Column(Integer, ForeignKey("stores.id"), nullable=False)
    quantity = Column(Float, nullable=False)
    usage_date = Column(Date, default=date.today)
    operator_id = Column(Integer, ForeignKey("users.id"))
    receiver = Column(String(100), nullable=False)
    remark = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)

    material = relationship("Material", back_populates="usage_records")


class TransferRecord(Base):
    __tablename__ = "transfer_records"

    id = Column(Integer, primary_key=True, index=True)
    material_id = Column(Integer, ForeignKey("materials.id"), nullable=False)
    from_store_id = Column(Integer, ForeignKey("stores.id"), nullable=False)
    to_store_id = Column(Integer, ForeignKey("stores.id"), nullable=False)
    quantity = Column(Float, nullable=False)
    transfer_date = Column(Date, default=date.today)
    operator_id = Column(Integer, ForeignKey("users.id"))
    batch_number = Column(String(100))
    remark = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)

    material = relationship("Material")
    from_store = relationship("Store", foreign_keys=[from_store_id])
    to_store = relationship("Store", foreign_keys=[to_store_id])
