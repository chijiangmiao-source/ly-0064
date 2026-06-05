from litestar import Litestar, get
from litestar.config.cors import CORSConfig
from litestar.openapi import OpenAPIConfig, OpenAPIController

from app.database import Base, engine
from app.routers.auth import AuthController
from app.routers.stores import StoreController
from app.routers.categories import CategoryController
from app.routers.materials import MaterialController
from app.routers.stock_ins import StockInController
from app.routers.open_records import OpenRecordController
from app.routers.damage_records import DamageRecordController
from app.routers.dashboard import DashboardController


Base.metadata.create_all(bind=engine)

cors_config = CORSConfig(
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)


class CustomOpenAPIController(OpenAPIController):
    path = "/docs"


@get("/")
async def root() -> dict:
    return {"message": "奶茶店原料管理系统 API"}


app = Litestar(
    route_handlers=[
        root,
        AuthController,
        StoreController,
        CategoryController,
        MaterialController,
        StockInController,
        OpenRecordController,
        DamageRecordController,
        DashboardController,
    ],
    cors_config=cors_config,
    openapi_config=OpenAPIConfig(
        title="奶茶店原料管理系统 API",
        version="1.0.0",
        openapi_controller=CustomOpenAPIController,
    ),
)
