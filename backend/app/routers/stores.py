from typing import List
from litestar.controller import Controller
from litestar.di import Provide
from litestar.exceptions import NotFoundException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Store
from app.schemas import StoreCreate, StoreResponse
from app.dependencies import get_current_admin_user


class StoreController(Controller):
    path = "/stores"
    dependencies = {"db": Provide(get_db)}

    async def get_list(self, db: Session) -> List[StoreResponse]:
        stores = db.query(Store).all()
        return [StoreResponse.model_validate(s) for s in stores]

    async def get_detail(self, store_id: int, db: Session) -> StoreResponse:
        store = db.query(Store).filter(Store.id == store_id).first()
        if not store:
            raise NotFoundException("Store not found")
        return StoreResponse.model_validate(store)

    async def create(self, data: StoreCreate, db: Session) -> StoreResponse:
        store = Store(**data.model_dump())
        db.add(store)
        db.commit()
        db.refresh(store)
        return StoreResponse.model_validate(store)

    async def update(self, store_id: int, data: StoreCreate, db: Session) -> StoreResponse:
        store = db.query(Store).filter(Store.id == store_id).first()
        if not store:
            raise NotFoundException("Store not found")
        for key, value in data.model_dump().items():
            setattr(store, key, value)
        db.commit()
        db.refresh(store)
        return StoreResponse.model_validate(store)

    async def delete(self, store_id: int, db: Session) -> None:
        store = db.query(Store).filter(Store.id == store_id).first()
        if not store:
            raise NotFoundException("Store not found")
        db.delete(store)
        db.commit()
