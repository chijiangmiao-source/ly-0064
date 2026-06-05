from typing import List, Optional
from datetime import date
from litestar.controller import Controller
from litestar.di import Provide
from litestar.exceptions import NotFoundException, ClientException
from litestar.params import Parameter
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import UsageRecord, Material, User, Store
from app.schemas import UsageRecordCreate, UsageRecordResponse
from app.dependencies import get_current_user


class UsageRecordController(Controller):
    path = "/usage-records"
    dependencies = {"db": Provide(get_db), "current_user": Provide(get_current_user)}

    async def get_list(
        self,
        db: Session,
        material_id: Optional[int] = Parameter(default=None),
        store_id: Optional[int] = Parameter(default=None),
        start_date: Optional[str] = Parameter(default=None),
        end_date: Optional[str] = Parameter(default=None),
        receiver: Optional[str] = Parameter(default=None),
    ) -> List[UsageRecordResponse]:
        query = db.query(UsageRecord)
        if material_id:
            query = query.filter(UsageRecord.material_id == material_id)
        if store_id:
            query = query.filter(UsageRecord.store_id == store_id)
        if start_date:
            query = query.filter(UsageRecord.usage_date >= start_date)
        if end_date:
            query = query.filter(UsageRecord.usage_date <= end_date)
        if receiver:
            query = query.filter(UsageRecord.receiver.contains(receiver))

        records = query.order_by(UsageRecord.created_at.desc()).all()
        return [UsageRecordResponse.model_validate(r) for r in records]

    async def create(self, data: UsageRecordCreate, db: Session, current_user: User) -> UsageRecordResponse:
        material = db.query(Material).filter(Material.id == data.material_id).first()
        if not material:
            raise NotFoundException("原料不存在")

        store = db.query(Store).filter(Store.id == data.store_id).first()
        if not store:
            raise NotFoundException("门店不存在")

        if material.store_id and material.store_id != data.store_id:
            raise ClientException("该原料不属于所选门店，不能领用")

        usage_date = data.usage_date or date.today()

        if material.expiry_date and usage_date > material.expiry_date:
            raise ClientException("该原料在领用日期已过期，不能领用")

        if material.open_status and material.expiry_date and usage_date > material.expiry_date:
            raise ClientException("该原料已开封并在领用日期已失效，不能领用")

        if data.quantity > material.stock_quantity:
            raise ClientException("领用数量不能超过当前库存")

        if material.stock_quantity <= 0:
            raise ClientException("该原料库存不足")

        record = UsageRecord(
            **data.model_dump(exclude_unset=True),
            operator_id=current_user.id
        )
        if not record.usage_date:
            record.usage_date = date.today()

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
        return UsageRecordResponse.model_validate(record)

    async def delete(self, record_id: int, db: Session) -> None:
        record = db.query(UsageRecord).filter(UsageRecord.id == record_id).first()
        if not record:
            raise NotFoundException("领用记录不存在")

        material = db.query(Material).filter(Material.id == record.material_id).first()
        if material:
            material.stock_quantity += record.quantity

        db.delete(record)
        db.commit()
