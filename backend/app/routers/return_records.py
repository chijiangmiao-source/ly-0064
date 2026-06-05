from typing import List, Optional
from datetime import date
from litestar.controller import Controller
from litestar.di import Provide
from litestar.exceptions import NotFoundException, ClientException
from litestar.params import Parameter
from litestar.handlers import get, post, delete
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import ReturnRecord, Material, User, Store
from app.schemas import ReturnRecordCreate, ReturnRecordResponse
from app.dependencies import get_current_user


class ReturnRecordController(Controller):
    path = "/return-records"
    dependencies = {"db": Provide(get_db), "current_user": Provide(get_current_user)}

    @get("/")
    async def get_list(
        self,
        db: Session,
        store_id: Optional[int] = Parameter(default=None),
        material_id: Optional[int] = Parameter(default=None),
        batch_number: Optional[str] = Parameter(default=None),
        start_date: Optional[str] = Parameter(default=None),
        end_date: Optional[str] = Parameter(default=None),
    ) -> List[ReturnRecordResponse]:
        query = db.query(ReturnRecord)
        if store_id:
            query = query.filter(ReturnRecord.store_id == store_id)
        if material_id:
            query = query.filter(ReturnRecord.material_id == material_id)
        if batch_number:
            query = query.filter(ReturnRecord.batch_number == batch_number)
        if start_date:
            query = query.filter(ReturnRecord.return_date >= start_date)
        if end_date:
            query = query.filter(ReturnRecord.return_date <= end_date)

        records = query.order_by(ReturnRecord.created_at.desc()).all()
        return [ReturnRecordResponse.model_validate(r) for r in records]

    @post("/")
    async def create(
        self,
        data: ReturnRecordCreate,
        db: Session,
        current_user: User,
    ) -> ReturnRecordResponse:
        material = db.query(Material).filter(Material.id == data.material_id).first()
        if not material:
            raise NotFoundException("原料不存在")

        store = db.query(Store).filter(Store.id == data.store_id).first()
        if not store:
            raise NotFoundException("门店不存在")

        if data.quantity > material.stock_quantity:
            raise ClientException("退货数量不能超过当前库存")

        today = date.today()
        is_expired = material.expiry_date and today > material.expiry_date
        if material.open_status and not is_expired:
            raise ClientException("已开封且未失效的原料不能退回供应商")

        if material.batch_number and data.batch_number != material.batch_number:
            raise ClientException("不同批次原料必须分开退货，请选择对应批次的原料")

        record = ReturnRecord(
            **data.model_dump(exclude_unset=True),
            operator_id=current_user.id,
        )
        if not record.return_date:
            record.return_date = date.today()

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
        return ReturnRecordResponse.model_validate(record)

    @delete("/{record_id:int}")
    async def delete(self, record_id: int, db: Session) -> None:
        record = db.query(ReturnRecord).filter(ReturnRecord.id == record_id).first()
        if not record:
            raise NotFoundException("退货记录不存在")

        material = db.query(Material).filter(Material.id == record.material_id).first()
        if material:
            material.stock_quantity += record.quantity

        db.delete(record)
        db.commit()
