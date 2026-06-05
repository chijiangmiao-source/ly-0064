from typing import List
from datetime import date, timedelta
from litestar.controller import Controller
from litestar.di import Provide
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models import Material, DamageRecord, MaterialCategory
from app.schemas import (
    DashboardStats,
    ExpiryWarningResponse,
    DamageRankingResponse,
    CategoryStockResponse
)


class DashboardController(Controller):
    path = "/dashboard"
    dependencies = {"db": Provide(get_db)}

    async def get_stats(self, db: Session) -> DashboardStats:
        today = date.today()
        warning_days = 3
        
        expiring_soon_count = db.query(Material).filter(
            Material.expiry_date.isnot(None),
            Material.expiry_date > today,
            Material.expiry_date <= today + timedelta(days=warning_days)
        ).count()
        
        expired_count = db.query(Material).filter(
            Material.expiry_date.isnot(None),
            Material.expiry_date < today
        ).count()
        
        total_materials = db.query(Material).count()
        total_stock = db.query(func.sum(Material.stock_quantity)).scalar() or 0
        
        damage_ranking_data = db.query(
            DamageRecord.material_id,
            Material.name,
            Material.code,
            func.sum(DamageRecord.quantity).label('total_damage'),
            func.count(DamageRecord.id).label('damage_count')
        ).join(Material).group_by(
            DamageRecord.material_id,
            Material.name,
            Material.code
        ).order_by(func.sum(DamageRecord.quantity).desc()).limit(10).all()
        
        damage_ranking = [
            DamageRankingResponse(
                material_id=row.material_id,
                material_name=row.name,
                material_code=row.code,
                total_damage=row.total_damage,
                damage_count=row.damage_count
            ) for row in damage_ranking_data
        ]
        
        category_stock_data = db.query(
            MaterialCategory.id,
            MaterialCategory.name,
            func.sum(Material.stock_quantity).label('total_stock'),
            func.count(Material.id).label('material_count')
        ).select_from(MaterialCategory).join(
            Material, Material.category_id == MaterialCategory.id, isouter=True
        ).group_by(
            MaterialCategory.id,
            MaterialCategory.name
        ).all()
        
        category_stock = [
            CategoryStockResponse(
                category_id=row.id,
                category_name=row.name,
                total_stock=row.total_stock or 0,
                material_count=row.material_count or 0
            ) for row in category_stock_data
        ]
        
        return DashboardStats(
            expiring_soon_count=expiring_soon_count,
            expired_count=expired_count,
            total_materials=total_materials,
            total_stock=total_stock,
            damage_ranking=damage_ranking,
            category_stock=category_stock
        )

    async def get_expiry_warnings(self, db: Session) -> List[ExpiryWarningResponse]:
        today = date.today()
        warning_days = 7
        
        materials = db.query(Material).filter(
            Material.expiry_date.isnot(None),
            Material.expiry_date <= today + timedelta(days=warning_days)
        ).order_by(Material.expiry_date).all()
        
        result = []
        for m in materials:
            days_remaining = (m.expiry_date - today).days
            result.append(ExpiryWarningResponse(
                id=m.id,
                code=m.code,
                name=m.name,
                expiry_date=m.expiry_date,
                days_remaining=days_remaining,
                current_status=m.current_status
            ))
        
        return result
