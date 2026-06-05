from typing import List
from litestar.controller import Controller
from litestar.di import Provide
from litestar.exceptions import NotFoundException, ClientException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app.models import MaterialCategory
from app.schemas import MaterialCategoryCreate, MaterialCategoryResponse


class CategoryController(Controller):
    path = "/categories"
    dependencies = {"db": Provide(get_db)}

    async def get_list(self, db: Session) -> List[MaterialCategoryResponse]:
        categories = db.query(MaterialCategory).all()
        return [MaterialCategoryResponse.model_validate(c) for c in categories]

    async def get_detail(self, category_id: int, db: Session) -> MaterialCategoryResponse:
        category = db.query(MaterialCategory).filter(MaterialCategory.id == category_id).first()
        if not category:
            raise NotFoundException("Category not found")
        return MaterialCategoryResponse.model_validate(category)

    async def create(self, data: MaterialCategoryCreate, db: Session) -> MaterialCategoryResponse:
        category = MaterialCategory(**data.model_dump())
        try:
            db.add(category)
            db.commit()
            db.refresh(category)
        except IntegrityError:
            db.rollback()
            raise ClientException("分类名称已存在")
        return MaterialCategoryResponse.model_validate(category)

    async def update(self, category_id: int, data: MaterialCategoryCreate, db: Session) -> MaterialCategoryResponse:
        category = db.query(MaterialCategory).filter(MaterialCategory.id == category_id).first()
        if not category:
            raise NotFoundException("Category not found")
        for key, value in data.model_dump().items():
            setattr(category, key, value)
        try:
            db.commit()
            db.refresh(category)
        except IntegrityError:
            db.rollback()
            raise ClientException("分类名称已存在")
        return MaterialCategoryResponse.model_validate(category)

    async def delete(self, category_id: int, db: Session) -> None:
        category = db.query(MaterialCategory).filter(MaterialCategory.id == category_id).first()
        if not category:
            raise NotFoundException("Category not found")
        db.delete(category)
        db.commit()
