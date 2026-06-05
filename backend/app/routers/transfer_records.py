from typing import List, Optional
from datetime import date
from litestar.controller import Controller
from litestar.di import Provide
from litestar.exceptions import NotFoundException, ClientException
from litestar.params import Parameter
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import TransferRecord, Material, User, Store
from app.schemas import TransferRecordCreate, TransferRecordResponse
from app.dependencies import get_current_user


class TransferRecordController(Controller):
    path = "/transfer-records"
    dependencies = {"db": Provide(get_db), "current_user": Provide(get_current_user)}

    async def get_list(
        self,
        db: Session,
        from_store_id: Optional[int] = Parameter(default=None),
        to_store_id: Optional[int] = Parameter(default=None),
        material_id: Optional[int] = Parameter(default=None),
        start_date: Optional[str] = Parameter(default=None),
        end_date: Optional[str] = Parameter(default=None),
    ) -> List[TransferRecordResponse]:
        query = db.query(TransferRecord)
        if from_store_id:
            query = query.filter(TransferRecord.from_store_id == from_store_id)
        if to_store_id:
            query = query.filter(TransferRecord.to_store_id == to_store_id)
        if material_id:
            query = query.filter(TransferRecord.material_id == material_id)
        if start_date:
            query = query.filter(TransferRecord.transfer_date >= start_date)
        if end_date:
            query = query.filter(TransferRecord.transfer_date <= end_date)

        records = query.order_by(TransferRecord.created_at.desc()).all()
        return [TransferRecordResponse.model_validate(r) for r in records]

    async def create(
        self, data: TransferRecordCreate, db: Session, current_user: User
    ) -> TransferRecordResponse:
        from_store = db.query(Store).filter(Store.id == data.from_store_id).first()
        if not from_store:
            raise NotFoundException("调出门店不存在")

        to_store = db.query(Store).filter(Store.id == data.to_store_id).first()
        if not to_store:
            raise NotFoundException("调入门店不存在")

        if data.from_store_id == data.to_store_id:
            raise ClientException("调出门店和调入门店不能相同")

        material = (
            db.query(Material)
            .filter(
                Material.id == data.material_id,
                Material.store_id == data.from_store_id,
            )
            .first()
        )
        if not material:
            raise ClientException("该原料不属于调出门店，不能调拨")

        transfer_date = data.transfer_date or date.today()

        if material.expiry_date and transfer_date > material.expiry_date:
            raise ClientException("该原料已过期，不能调拨")

        if material.open_status:
            raise ClientException("已开封的原料不能调拨")

        if material.stock_quantity <= 0:
            raise ClientException("该原料库存不足，不能调拨")

        if data.quantity > material.stock_quantity:
            raise ClientException("调拨数量不能超过调出门店当前库存")

        record = TransferRecord(
            **data.model_dump(exclude_unset=True),
            operator_id=current_user.id,
        )
        if not record.transfer_date:
            record.transfer_date = date.today()

        db.add(record)

        material.stock_quantity -= data.quantity
        if material.stock_quantity <= 0:
            material.stock_quantity = 0
            material.open_status = False
            material.open_date = None

        target_material = (
            db.query(Material)
            .filter(
                Material.code == material.code,
                Material.store_id == data.to_store_id,
            )
            .first()
        )

        if target_material:
            target_material.stock_quantity += data.quantity
            if not target_material.expiry_date and material.expiry_date:
                target_material.expiry_date = material.expiry_date
        else:
            new_material = Material(
                code=material.code,
                name=material.name,
                specification=material.specification,
                category_id=material.category_id,
                store_id=data.to_store_id,
                stock_quantity=data.quantity,
                open_status=False,
                open_date=None,
                expiry_date=material.expiry_date,
                shelf_life_days=material.shelf_life_days,
            )
            db.add(new_material)

        db.commit()
        db.refresh(record)
        return TransferRecordResponse.model_validate(record)

    async def delete(self, record_id: int, db: Session) -> None:
        record = (
            db.query(TransferRecord).filter(TransferRecord.id == record_id).first()
        )
        if not record:
            raise NotFoundException("调拨记录不存在")

        from_material = (
            db.query(Material)
            .filter(
                Material.id == record.material_id,
                Material.store_id == record.from_store_id,
            )
            .first()
        )
        if from_material:
            from_material.stock_quantity += record.quantity

        to_material = (
            db.query(Material)
            .filter(
                Material.code == from_material.code if from_material else None,
                Material.store_id == record.to_store_id,
            )
            .first()
        )
        if to_material:
            to_material.stock_quantity -= record.quantity
            if to_material.stock_quantity < 0:
                to_material.stock_quantity = 0

        db.delete(record)
        db.commit()
