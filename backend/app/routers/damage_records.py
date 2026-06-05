from typing import List, Optional
from datetime import date
from litestar.controller import Controller
from litestar.di import Provide
from litestar.exceptions import NotFoundException, ClientException
from litestar.params import Parameter
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models import DamageRecord, Material, User
from app.schemas import DamageRecordCreate, DamageRecordResponse
from app.dependencies import get_current_user


class DamageRecordController(Controller):
    path = "/damage-records"
    dependencies = {"db": Provide(get_db), "current_user": Provide(get_current_user)}

    async def get_list(
        self,
        db: Session,
        material_id: Optional[int] = Parameter(default=None),
        start_date: Optional[str] = Parameter(default=None),
        end_date: Optional[str] = Parameter(default=None),
    ) -> List[DamageRecordResponse]:
        query = db.query(DamageRecord)
        if material_id:
            query = query.filter(DamageRecord.material_id == material_id)
        if start_date:
            query = query.filter(DamageRecord.damage_date >= start_date)
        if end_date:
            query = query.filter(DamageRecord.damage_date <= end_date)
        
        records = query.order_by(DamageRecord.created_at.desc()).all()
        return [DamageRecordResponse.model_validate(r) for r in records]

    async def create(self, data: DamageRecordCreate, db: Session, current_user: User) -> DamageRecordResponse:
        material = db.query(Material).filter(Material.id == data.material_id).first()
        if not material:
            raise NotFoundException("Material not found")
        
        if data.quantity > material.stock_quantity:
            raise ClientException("报损数量不能超过当前库存")
        
        record = DamageRecord(
            **data.model_dump(exclude_unset=True),
            operator_id=current_user.id
        )
        if not record.damage_date:
            record.damage_date = date.today()
        
        db.add(record)
        
        material.stock_quantity -= data.quantity
        if material.stock_quantity <= 0:
            material.stock_quantity = 0
            material.open_status = False
            material.open_date = None
            material.expiry_date = None
            material.batch_number = None
        
        db.commit()
        db.refresh(record)
        return DamageRecordResponse.model_validate(record)

    async def delete(self, record_id: int, db: Session) -> None:
        record = db.query(DamageRecord).filter(DamageRecord.id == record_id).first()
        if not record:
            raise NotFoundException("Damage record not found")
        
        material = db.query(Material).filter(Material.id == record.material_id).first()
        if material:
            material.stock_quantity += record.quantity
        
        db.delete(record)
        db.commit()
