from typing import List
from datetime import date, timedelta
from litestar.controller import Controller
from litestar.di import Provide
from sqlalchemy.orm import Session
from sqlalchemy import func, cast, Date

from app.database import get_db
from app.models import Material, DamageRecord, MaterialCategory, UsageRecord, TransferRecord, ReturnRecord
from app.schemas import (
    DashboardStats,
    ExpiryWarningResponse,
    DamageRankingResponse,
    CategoryStockResponse,
    UsageTrendResponse,
    UsageRankingResponse,
    TransferTrendResponse,
    TransferRankingResponse,
    ReturnTrendResponse,
    ReturnRankingResponse
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

        today = date.today()
        seven_days_ago = today - timedelta(days=6)

        usage_trend_data = db.query(
            cast(UsageRecord.usage_date, Date).label('usage_date'),
            func.sum(UsageRecord.quantity).label('total_quantity'),
            func.count(UsageRecord.id).label('record_count')
        ).filter(
            UsageRecord.usage_date >= seven_days_ago,
            UsageRecord.usage_date <= today
        ).group_by(
            cast(UsageRecord.usage_date, Date)
        ).all()

        usage_trend_map = {}
        for row in usage_trend_data:
            usage_trend_map[row.usage_date.isoformat()] = UsageTrendResponse(
                date=row.usage_date.isoformat(),
                total_quantity=row.total_quantity or 0,
                record_count=row.record_count or 0
            )

        usage_trend = []
        for i in range(7):
            d = today - timedelta(days=6 - i)
            date_str = d.isoformat()
            if date_str in usage_trend_map:
                usage_trend.append(usage_trend_map[date_str])
            else:
                usage_trend.append(UsageTrendResponse(
                    date=date_str,
                    total_quantity=0,
                    record_count=0
                ))

        usage_ranking_data = db.query(
            UsageRecord.material_id,
            Material.name,
            Material.code,
            func.sum(UsageRecord.quantity).label('total_quantity'),
            func.count(UsageRecord.id).label('usage_count')
        ).join(Material).group_by(
            UsageRecord.material_id,
            Material.name,
            Material.code
        ).order_by(func.sum(UsageRecord.quantity).desc()).limit(10).all()

        usage_ranking = [
            UsageRankingResponse(
                material_id=row.material_id,
                material_name=row.name,
                material_code=row.code,
                total_quantity=row.total_quantity or 0,
                usage_count=row.usage_count or 0
            ) for row in usage_ranking_data
        ]

        transfer_trend_data = db.query(
            cast(TransferRecord.transfer_date, Date).label('transfer_date'),
            func.sum(TransferRecord.quantity).label('total_quantity'),
            func.count(TransferRecord.id).label('record_count')
        ).filter(
            TransferRecord.transfer_date >= seven_days_ago,
            TransferRecord.transfer_date <= today
        ).group_by(
            cast(TransferRecord.transfer_date, Date)
        ).all()

        transfer_trend_map = {}
        for row in transfer_trend_data:
            transfer_trend_map[row.transfer_date.isoformat()] = TransferTrendResponse(
                date=row.transfer_date.isoformat(),
                total_quantity=row.total_quantity or 0,
                record_count=row.record_count or 0
            )

        transfer_trend = []
        for i in range(7):
            d = today - timedelta(days=6 - i)
            date_str = d.isoformat()
            if date_str in transfer_trend_map:
                transfer_trend.append(transfer_trend_map[date_str])
            else:
                transfer_trend.append(TransferTrendResponse(
                    date=date_str,
                    total_quantity=0,
                    record_count=0
                ))

        transfer_ranking_data = db.query(
            TransferRecord.material_id,
            Material.name,
            Material.code,
            func.sum(TransferRecord.quantity).label('total_quantity'),
            func.count(TransferRecord.id).label('transfer_count')
        ).join(Material).group_by(
            TransferRecord.material_id,
            Material.name,
            Material.code
        ).order_by(func.sum(TransferRecord.quantity).desc()).limit(10).all()

        transfer_ranking = [
            TransferRankingResponse(
                material_id=row.material_id,
                material_name=row.name,
                material_code=row.code,
                total_quantity=row.total_quantity or 0,
                transfer_count=row.transfer_count or 0
            ) for row in transfer_ranking_data
        ]

        return_trend_data = db.query(
            cast(ReturnRecord.return_date, Date).label('return_date'),
            func.sum(ReturnRecord.quantity).label('total_quantity'),
            func.count(ReturnRecord.id).label('record_count')
        ).filter(
            ReturnRecord.return_date >= seven_days_ago,
            ReturnRecord.return_date <= today
        ).group_by(
            cast(ReturnRecord.return_date, Date)
        ).all()

        return_trend_map = {}
        for row in return_trend_data:
            return_trend_map[row.return_date.isoformat()] = ReturnTrendResponse(
                date=row.return_date.isoformat(),
                total_quantity=row.total_quantity or 0,
                record_count=row.record_count or 0
            )

        return_trend = []
        for i in range(7):
            d = today - timedelta(days=6 - i)
            date_str = d.isoformat()
            if date_str in return_trend_map:
                return_trend.append(return_trend_map[date_str])
            else:
                return_trend.append(ReturnTrendResponse(
                    date=date_str,
                    total_quantity=0,
                    record_count=0
                ))

        return_ranking_data = db.query(
            ReturnRecord.material_id,
            Material.name,
            Material.code,
            func.sum(ReturnRecord.quantity).label('total_quantity'),
            func.count(ReturnRecord.id).label('return_count')
        ).join(Material).group_by(
            ReturnRecord.material_id,
            Material.name,
            Material.code
        ).order_by(func.sum(ReturnRecord.quantity).desc()).limit(10).all()

        return_ranking = [
            ReturnRankingResponse(
                material_id=row.material_id,
                material_name=row.name,
                material_code=row.code,
                total_quantity=row.total_quantity or 0,
                return_count=row.return_count or 0
            ) for row in return_ranking_data
        ]

        return DashboardStats(
            expiring_soon_count=expiring_soon_count,
            expired_count=expired_count,
            total_materials=total_materials,
            total_stock=total_stock,
            damage_ranking=damage_ranking,
            category_stock=category_stock,
            usage_trend=usage_trend,
            usage_ranking=usage_ranking,
            transfer_trend=transfer_trend,
            transfer_ranking=transfer_ranking,
            return_trend=return_trend,
            return_ranking=return_ranking
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
