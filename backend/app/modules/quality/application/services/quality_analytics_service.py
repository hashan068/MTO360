"""
Quality Analytics Service - Application Layer
Business logic for quality metrics and analytics
"""
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy.orm import Session

from app.modules.quality.infra.repositories import (
    InspectionResultRepository,
    DefectRepository,
    NCRRepository,
    ReworkOperationRepository,
    CAPARepository,
    QualityHoldRepository,
)


class QualityAnalyticsService:
    """Service for quality metrics, analytics, and dashboard data"""
    
    def __init__(self, db: Session):
        self.db = db
        self.inspection_repo = InspectionResultRepository(db)
        self.defect_repo = DefectRepository(db)
        self.ncr_repo = NCRRepository(db)
        self.rework_repo = ReworkOperationRepository(db)
        self.capa_repo = CAPARepository(db)
        self.hold_repo = QualityHoldRepository(db)
    
    # ========== Key Quality Metrics ==========
    
    def calculate_first_pass_yield(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Calculate First Pass Yield (FPY)
        FPY = (Units passing first inspection / Total units inspected) * 100
        """
        pass_rate = self.inspection_repo.calculate_pass_rate(
            start_date=start_date,
            end_date=end_date
        )
        
        total = pass_rate['total']
        passed = pass_rate['passed']
        
        fpy = (passed / total * 100) if total > 0 else 0
        
        return {
            "first_pass_yield": round(fpy, 2),
            "units_inspected": total,
            "units_passed_first_time": passed,
            "units_failed": pass_rate['failed'],
            "units_conditional": pass_rate['conditional'],
            "period": {
                "start_date": start_date.isoformat() if start_date else None,
                "end_date": end_date.isoformat() if end_date else None
            }
        }
    
    def calculate_defect_rate(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        per_units: int = 1000
    ) -> Dict[str, Any]:
        """
        Calculate defect rate (defects per X units)
        Default: DPMO (Defects Per Million Opportunities)
        """
        filters = {}
        if start_date:
            filters['date_from'] = start_date
        if end_date:
            filters['date_to'] = end_date
        
        defects = self.defect_repo.search(**filters)
        
        total_defects = len(defects)
        total_affected = sum(d.quantity_affected for d in defects)
        
        # Simplified: using inspections as opportunities
        inspections = self.inspection_repo.calculate_pass_rate(
            start_date=start_date,
            end_date=end_date
        )
        opportunities = inspections['total']
        
        defect_rate = (total_defects / opportunities * per_units) if opportunities > 0 else 0
        
        return {
            "defect_rate": round(defect_rate, 2),
            "total_defects": total_defects,
            "total_quantity_affected": total_affected,
            "opportunities": opportunities,
            "per_units": per_units,
            "period": {
                "start_date": start_date.isoformat() if start_date else None,
                "end_date": end_date.isoformat() if end_date else None
            }
        }
    
    def calculate_cost_of_quality(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Calculate total Cost of Quality (COQ)
        Categories:
        - Internal failure costs (rework, scrap)
        - External failure costs (customer returns)
        - Appraisal costs (inspection)
        - Prevention costs (CAPA implementation)
        """
        # NCR costs (internal failures)
        ncr_metrics = self.ncr_repo.calculate_metrics(
            start_date=start_date,
            end_date=end_date
        )
        internal_failure_cost = ncr_metrics['costs']['total']
        
        # Rework costs
        rework_stats = self.rework_repo.get_statistics(
            start_date=start_date,
            end_date=end_date
        )
        rework_cost = rework_stats['total_cost']
        
        # TODO: Add appraisal and prevention costs
        appraisal_cost = 0  # Inspection labor costs
        prevention_cost = 0  # CAPA implementation costs
        
        total_coq = internal_failure_cost + rework_cost + appraisal_cost + prevention_cost
        
        return {
            "total_cost_of_quality": float(total_coq),
            "breakdown": {
                "internal_failure": float(internal_failure_cost),
                "rework": float(rework_cost),
                "appraisal": float(appraisal_cost),
                "prevention": float(prevention_cost)
            },
            "ncr_count": ncr_metrics['total'],
            "rework_count": rework_stats['total'],
            "period": {
                "start_date": start_date.isoformat() if start_date else None,
                "end_date": end_date.isoformat() if end_date else None
            }
        }
    
    def calculate_rework_rate(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Calculate rework rate"""
        rework_stats = self.rework_repo.get_statistics(
            start_date=start_date,
            end_date=end_date
        )
        
        # Get total inspections as denominator
        inspections = self.inspection_repo.calculate_pass_rate(
            start_date=start_date,
            end_date=end_date
        )
        
        rework_rate = (rework_stats['total'] / inspections['total'] * 100) if inspections['total'] > 0 else 0
        
        return {
            "rework_rate": round(rework_rate, 2),
            "total_rework_operations": rework_stats['total'],
            "total_inspections": inspections['total'],
            "avg_rework_duration_hours": round(rework_stats['avg_duration_minutes'] / 60, 1),
            "total_rework_cost": rework_stats['total_cost']
        }
    
    def calculate_scrap_rate(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Calculate scrap rate from NCR dispositions"""
        filters = {
            'disposition': 'scrap',
            'date_from': start_date,
            'date_to': end_date
        }
        
        ncrs = self.ncr_repo.search(**filters)
        
        total_scrapped = sum(ncr.quantity_affected for ncr in ncrs)
        total_scrap_cost = sum(ncr.scrap_cost or Decimal('0') for ncr in ncrs)
        
        return {
            "scrap_count": len(ncrs),
            "total_quantity_scrapped": total_scrapped,
            "total_scrap_cost": float(total_scrap_cost)
        }
    
    # ========== Dashboard Data ==========
    
    def get_quality_dashboard(
        self,
        days_back: int = 30
    ) -> Dict[str, Any]:
        """
        Get comprehensive quality dashboard data
        Includes all key metrics, trends, and alerts
        """
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days_back)
        
        # Key metrics
        fpy = self.calculate_first_pass_yield(start_date, end_date)
        defect_rate_data = self.calculate_defect_rate(start_date, end_date, per_units=1000)
        coq = self.calculate_cost_of_quality(start_date, end_date)
        rework_rate_data = self.calculate_rework_rate(start_date, end_date)
        
        # Current status
        ncr_metrics = self.ncr_repo.calculate_metrics()
        capa_metrics = self.capa_repo.calculate_metrics()
        defect_stats = self.defect_repo.get_statistics()
        
        # Overdue items
        overdue_ncrs = self.ncr_repo.get_overdue()
        overdue_capas = self.capa_repo.get_overdue()
        
        # Active holds
        active_holds = self.hold_repo.get_active()
        
        # Recent defects (last 10)
        recent_defects = self.defect_repo.get_all(skip=0, limit=10)
        
        # Recent NCRs (last 10)
        recent_ncrs = self.ncr_repo.get_all(skip=0, limit=10)
        
        return {
            "summary": {
                "first_pass_yield": fpy['first_pass_yield'],
                "defect_rate": defect_rate_data['defect_rate'],
                "cost_of_quality": coq['total_cost_of_quality'],
                "rework_rate": rework_rate_data['rework_rate'],
                "open_ncrs": ncr_metrics['by_status']['open'],
                "open_capas": capa_metrics['by_status']['open'],
                "active_holds": len(active_holds)
            },
            "alerts": {
                "overdue_ncrs": len(overdue_ncrs),
                "overdue_capas": len(overdue_capas),
                "critical_defects": defect_stats['by_severity']['critical']
            },
            "trends": {
                "defect_breakdown": defect_stats['by_severity'],
                "ncr_status_breakdown": ncr_metrics['by_status'],
                "capa_status_breakdown": capa_metrics['by_status']
            },
            "recent_items": {
                "defects": [{"id": d.id, "defect_number": d.defect_number, "severity": d.severity.value} for d in recent_defects],
                "ncrs": [{"id": n.id, "ncr_number": n.ncr_number, "status": n.status.value} for n in recent_ncrs]
            },
            "period_days": days_back
        }
    
    # ========== Performance Analytics ==========
    
    def get_operator_quality_performance(
        self,
        operator_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get quality performance metrics for an operator"""
        # Get defects attributed to operator
        defects = self.defect_repo.get_by_operator(operator_id)
        
        if start_date or end_date:
            filtered_defects = [
                d for d in defects
                if (not start_date or d.created_at >= start_date) and
                   (not end_date or d.created_at <= end_date)
            ]
        else:
            filtered_defects = defects
        
        # Get inspections by this operator (need to get MO operations worked)
        # Simplified for now
        
        return {
            "operator_id": operator_id,
            "defects_found": len(filtered_defects),
            "defects_by_severity": {
                "critical": sum(1 for d in filtered_defects if d.severity.value == 'critical'),
                "major": sum(1 for d in filtered_defects if d.severity.value == 'major'),
                "minor": sum(1 for d in filtered_defects if d.severity.value == 'minor')
            },
            "period": {
                "start_date": start_date.isoformat() if start_date else None,
                "end_date": end_date.isoformat() if end_date else None
            }
        }
    
    def get_supplier_quality_performance(
        self,
        supplier_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get quality performance metrics for a supplier"""
        # Get defects from this supplier
        defects = self.defect_repo.get_by_supplier(supplier_id)
        
        if start_date or end_date:
            filtered_defects = [
                d for d in defects
                if (not start_date or d.created_at >= start_date) and
                   (not end_date or d.created_at <= end_date)
            ]
        else:
            filtered_defects = defects
        
        return {
            "supplier_id": supplier_id,
            "defects_found": len(filtered_defects),
            "defects_by_type": {
                "material": sum(1 for d in filtered_defects if d.defect_type.value == 'material'),
                "dimensional": sum(1 for d in filtered_defects if d.defect_type.value == 'dimensional')
            },
            "defects_by_severity": {
                "critical": sum(1 for d in filtered_defects if d.severity.value == 'critical'),
                "major": sum(1 for d in filtered_defects if d.severity.value == 'major')
            },
            "period": {
                "start_date": start_date.isoformat() if start_date else None,
                "end_date": end_date.isoformat() if end_date else None
            }
        }
    
    # ========== Trend Analysis ==========
    
    def get_quality_trends(
        self,
        metric: str,  # 'fpy', 'defect_rate', 'ncr_count'
        period: str = 'weekly',  # 'daily', 'weekly', 'monthly'
        weeks_back: int = 12
    ) -> List[Dict[str, Any]]:
        """
        Get quality trends over time
        Returns time-series data for charting
        """
        # TODO: Implement time-series grouping
        # For now, return simplified data
        
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(weeks=weeks_back)
        
        if metric == 'fpy':
            fpy = self.calculate_first_pass_yield(start_date, end_date)
            return [
                {
                    "period": "overall",
                    "value": fpy['first_pass_yield'],
                    "date": end_date.isoformat()
                }
            ]
        
        elif metric == 'defect_rate':
            dr = self.calculate_defect_rate(start_date, end_date)
            return [
                {
                    "period": "overall",
                    "value": dr['defect_rate'],
                    "date": end_date.isoformat()
                }
            ]
        
        return []
