from typing import List, Optional
from litestar.controller import Controller
from litestar.di import Provide
from litestar.exceptions import NotFoundException, ClientException
from litestar.params import Parameter
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import OpenRecord, Material, User
from app.schemas import OpenRecordCreate, OpenRecordResponse
from app.dependencies import get_current_user


class OpenRecordController(Controller):
    path = "/open-records"
    dependencies = {"db": Provide(get_db), "current_user": Provide(get_current_user)}

    async def get_list(
        self,
        db: Session,
        material_id: Optional[int] = Parameter(default=None),
        start_date: Optional[str] = Parameter(default=None),
        end_date: Optional[str] = Parameter(default=None),
    ) -> List[OpenRecordResponse]:
        query = db.query(OpenRecord)
        if material_id:
            query = query.filter(OpenRecord.material_id == material_id)
        if start_date:
            query = query.filter(OpenRecord.open_date >= start_date)
        if end_date:
            query = query.filter(OpenRecord.open_date <= end_date)
        
        records = query.order_by(OpenRecord.created_at.desc()).all()
        return [OpenRecordResponse.model_validate(r) for r in records]

    async def create(self, data: OpenRecordCreate, db: Session, current_user: User) -> OpenRecordResponse:
        material = db.query(Material).filter(Material.id == data.material_id).first()
        if not material:
            raise NotFoundException("Material not found")
        
        if data.expiry_date < data.open_date:
            raise ClientException("失效日期不能早于开封日期")
        
        if material.expiry_date and data.open_date > material.expiry_date:
            raise ClientException("已失效原料不能继续开封使用")
        
        existing = db.query(OpenRecord).filter(
            OpenRecord.material_id == data.material_id,
            OpenRecord.open_date == data.open_date
        ).first()
        if existing:
            raise ClientException("同一原料同一天不能重复录入开封记录")
        
        record = OpenRecord(**data.model_dump(), operator_id=current_user.id)
        db.add(record)
        
        material.open_status = True
        material.open_date = data.open_date
        material.expiry_date = data.expiry_date
        
        db.commit()
        db.refresh(record)
        return OpenRecordResponse.model_validate(record)

    async def delete(self, record_id: int, db: Session) -> None:
        record = db.query(OpenRecord).filter(OpenRecord.id == record_id).first()
        if not record:
            raise NotFoundException("Open record not found")
        
        material_id = record.material_id
        db.delete(record)
        db.commit()
        
        remaining = db.query(OpenRecord).filter(OpenRecord.material_id == material_id).count()
        if remaining == 0:
            material = db.query(Material).filter(Material.id == material_id).first()
            if material:
                material.open_status = False
                material.open_date = None
                db.commit()
