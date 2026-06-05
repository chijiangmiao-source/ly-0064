from typing import List, Optional
from litestar.controller import Controller
from litestar.di import Provide
from litestar.exceptions import NotFoundException
from litestar.params import Parameter
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import StockIn, Material, User
from app.schemas import StockInCreate, StockInResponse
from app.dependencies import get_current_user


class StockInController(Controller):
    path = "/stock-ins"
    dependencies = {"db": Provide(get_db), "current_user": Provide(get_current_user)}

    async def get_list(
        self,
        db: Session,
        material_id: Optional[int] = Parameter(default=None),
        start_date: Optional[str] = Parameter(default=None),
        end_date: Optional[str] = Parameter(default=None),
    ) -> List[StockInResponse]:
        query = db.query(StockIn)
        if material_id:
            query = query.filter(StockIn.material_id == material_id)
        if start_date:
            query = query.filter(StockIn.purchase_date >= start_date)
        if end_date:
            query = query.filter(StockIn.purchase_date <= end_date)
        
        stock_ins = query.order_by(StockIn.created_at.desc()).all()
        return [StockInResponse.model_validate(s) for s in stock_ins]

    async def create(self, data: StockInCreate, db: Session, current_user: User) -> StockInResponse:
        material = db.query(Material).filter(Material.id == data.material_id).first()
        if not material:
            raise NotFoundException("Material not found")
        
        stock_in = StockIn(**data.model_dump(), operator_id=current_user.id)
        db.add(stock_in)
        
        material.stock_quantity += data.quantity
        if data.expiry_date and not material.open_status:
            material.expiry_date = data.expiry_date
        if data.batch_number and not material.batch_number:
            material.batch_number = data.batch_number
        
        db.commit()
        db.refresh(stock_in)
        return StockInResponse.model_validate(stock_in)

    async def delete(self, stock_in_id: int, db: Session) -> None:
        stock_in = db.query(StockIn).filter(StockIn.id == stock_in_id).first()
        if not stock_in:
            raise NotFoundException("StockIn record not found")
        
        material = db.query(Material).filter(Material.id == stock_in.material_id).first()
        if material:
            material.stock_quantity -= stock_in.quantity
            if material.stock_quantity <= 0:
                material.stock_quantity = 0
                material.open_status = False
                material.open_date = None
                material.expiry_date = None
                material.batch_number = None
        
        db.delete(stock_in)
        db.commit()
