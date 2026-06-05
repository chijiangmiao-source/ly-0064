from typing import List, Optional
from datetime import date
from litestar.controller import Controller
from litestar.di import Provide
from litestar.exceptions import NotFoundException, ClientException
from litestar.params import Parameter
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import or_, and_

from app.database import get_db
from app.models import Material, MaterialCategory
from app.schemas import MaterialCreate, MaterialUpdate, MaterialResponse


class MaterialController(Controller):
    path = "/materials"
    dependencies = {"db": Provide(get_db)}

    async def get_list(
        self,
        db: Session,
        keyword: Optional[str] = Parameter(default=None),
        category_id: Optional[int] = Parameter(default=None),
        store_id: Optional[int] = Parameter(default=None),
        status: Optional[str] = Parameter(default=None),
    ) -> List[MaterialResponse]:
        query = db.query(Material).join(MaterialCategory, isouter=True)
        
        if keyword:
            query = query.filter(
                or_(
                    Material.code.contains(keyword),
                    Material.name.contains(keyword)
                )
            )
        if category_id:
            query = query.filter(Material.category_id == category_id)
        if store_id:
            query = query.filter(Material.store_id == store_id)
        
        materials = query.all()
        
        if status:
            materials = [m for m in materials if m.current_status == status]
        
        return [MaterialResponse.model_validate(m) for m in materials]

    async def get_detail(self, material_id: int, db: Session) -> MaterialResponse:
        material = db.query(Material).filter(Material.id == material_id).first()
        if not material:
            raise NotFoundException("Material not found")
        return MaterialResponse.model_validate(material)

    async def create(self, data: MaterialCreate, db: Session) -> MaterialResponse:
        material = Material(**data.model_dump())
        try:
            db.add(material)
            db.commit()
            db.refresh(material)
        except IntegrityError:
            db.rollback()
            raise ClientException("该门店下已存在相同编号和批次的原料")
        return MaterialResponse.model_validate(material)

    async def update(self, material_id: int, data: MaterialUpdate, db: Session) -> MaterialResponse:
        material = db.query(Material).filter(Material.id == material_id).first()
        if not material:
            raise NotFoundException("Material not found")
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(material, key, value)
        db.commit()
        db.refresh(material)
        return MaterialResponse.model_validate(material)

    async def delete(self, material_id: int, db: Session) -> None:
        material = db.query(Material).filter(Material.id == material_id).first()
        if not material:
            raise NotFoundException("Material not found")
        db.delete(material)
        db.commit()
