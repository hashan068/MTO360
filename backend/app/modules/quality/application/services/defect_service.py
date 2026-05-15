"""
Defect Service - Application Layer
Business logic for defect management and analytics
"""
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.models.quality import Defect, DefectStatusEnum
from app.schemas.quality import DefectCreate, DefectUpdate
from app.modules.quality.infra.repositories import DefectRepository


class DefectService:
    """Service for managing defects and defect analytics"""
    
    def __init__(self, db: Session):
        self.db = db
        self.defect_repo = DefectRepository(db)
    
    # ========== Defect Management ==========
    
    def create_defect(self, data: DefectCreate) -> Defect:
        """
        Create a new defect
        Business logic:
        - Auto-generates defect number
        - Validates context (MO, operation, etc.)
        - Can trigger NCR creation for critical defects
        """
        defect_data = data.model_dump()
        defect = self.defect_repo.create(**defect_data)
        
        # TODO: Trigger notification for critical defects
        if data.severity == 'critical':
            self._notify_critical_defect(defect)
        
        return defect
    
    def get_defect(self, defect_id: int) -> Optional[Defect]:
        """Get defect by ID"""
        return self.defect_repo.get_by_id(defect_id)
    
    def get_defect_by_number(self, defect_number: str) -> Optional[Defect]:
        """Get defect by number"""
        return self.defect_repo.get_by_number(defect_number)
    
    def list_defects(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[Defect]:
        """List all defects"""
        return self.defect_repo.get_all(skip=skip, limit=limit)
    
    def search_defects(self, **filters) -> List[Defect]:
        """
        Search defects with filters
        Supported filters:
        - defect_type, severity, status, responsible_party
        - manufacturing_order_id, operator_id, supplier_id
        - date_from, date_to, defect_category
        - skip, limit
        """
        return self.defect_repo.search(**filters)
    
    def update_defect(
        self,
        defect_id: int,
        data: DefectUpdate
    ) -> Optional[Defect]:
        """Update defect"""
        update_data = data.model_dump(exclude_unset=True)
        
        # Business logic: If status changes to resolved, auto-set resolved date
        if 'status' in update_data and update_data['status'] == DefectStatusEnum.RESOLVED:
            # Could add a resolved_date field if needed
            pass
        
        return self.defect_repo.update(defect_id, **update_data)
    
    def close_defect(self, defect_id: int) -> Optional[Defect]:
        """Close a defect (change status to closed)"""
        return self.defect_repo.update(
            defect_id,
            status=DefectStatusEnum.CLOSED
        )
    
    # ========== Defect Analytics ==========
    
    def get_defect_trends(
        self,
        group_by: str,  # 'type', 'severity', 'category', 'operator'
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Get defect trends grouped by specified field"""
        return self.defect_repo.get_defect_trends(
            group_by=group_by,
            start_date=start_date,
            end_date=end_date
        )
    
    def get_pareto_analysis(
        self,
        metric: str = 'defects',
        limit: int = 10,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        Get Pareto analysis (80/20 rule) for defects
        Helps identify top defect categories causing most issues
        """
        return self.defect_repo.get_pareto_analysis(
            metric=metric,
            limit=limit,
            start_date=start_date,
            end_date=end_date
        )
    
    def get_defect_statistics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get comprehensive defect statistics"""
        return self.defect_repo.get_statistics(
            start_date=start_date,
            end_date=end_date
        )
    
    def get_defects_by_mo(
        self,
        manufacturing_order_id: int
    ) -> List[Defect]:
        """Get all defects for a manufacturing order"""
        return self.defect_repo.get_by_mo(manufacturing_order_id)
    
    def get_defects_by_operator(
        self,
        operator_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Defect]:
        """Get defects by operator (for performance reviews)"""
        return self.defect_repo.get_by_operator(
            operator_id,
            skip=skip,
            limit=limit
        )
    
    def get_defects_by_supplier(
        self,
        supplier_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Defect]:
        """Get defects by supplier (for supplier quality rating)"""
        return self.defect_repo.get_by_supplier(
            supplier_id,
            skip=skip,
            limit=limit
        )
    
    # ========== Business Logic ==========
    
    def analyze_defect_patterns(
        self,
        manufacturing_order_id: Optional[int] = None,
        days_back: int = 30
    ) -> Dict[str, Any]:
        """
        Analyze defect patterns to identify recurring issues
        Returns insights for preventive actions
        """
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days_back)
        
        filters = {
            'date_from': start_date,
            'date_to': end_date
        }
        
        if manufacturing_order_id:
            filters['manufacturing_order_id'] = manufacturing_order_id
        
        defects = self.defect_repo.search(**filters)
        
        if not defects:
            return {
                "total_defects": 0,
                "recurring_categories": [],
                "severity_distribution": {},
                "recommendations": []
            }
        
        # Analyze categories
        category_counts = {}
        severity_counts = {}
        
        for defect in defects:
            category_counts[defect.defect_category] = category_counts.get(defect.defect_category, 0) + 1
            severity_counts[defect.severity.value] = severity_counts.get(defect.severity.value, 0) + 1
        
        # Identify recurring categories (appears 3+ times)
        recurring = [
            {"category": cat, "count": count}
            for cat, count in category_counts.items()
            if count >= 3
        ]
        recurring.sort(key=lambda x: x['count'], reverse=True)
        
        # Generate recommendations
        recommendations = []
        if recurring:
            recommendations.append(
                f"Consider CAPA for recurring defect category: {recurring[0]['category']} ({recurring[0]['count']} occurrences)"
            )
        
        if severity_counts.get('critical', 0) > 0:
            recommendations.append(
                f"Immediate attention required: {severity_counts['critical']} critical defects detected"
            )
        
        return {
            "total_defects": len(defects),
            "recurring_categories": recurring,
            "severity_distribution": severity_counts,
            "category_breakdown": category_counts,
            "recommendations": recommendations
        }
    
    def calculate_defect_rate(
        self,
        manufacturing_order_id: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        per_units: int = 1000
    ) -> float:
        """
        Calculate defect rate (defects per X units)
        Default: defects per 1000 units
        """
        filters = {}
        if start_date:
            filters['date_from'] = start_date
        if end_date:
            filters['date_to'] = end_date
        if manufacturing_order_id:
            filters['manufacturing_order_id'] = manufacturing_order_id
        
        defects = self.defect_repo.search(**filters)
        
        total_defects = len(defects)
        total_quantity = sum(d.quantity_affected for d in defects) if defects else 0
        
        # This would ideally be calculated against units produced
        # For now, simplified calculation
        if total_quantity == 0:
            return 0.0
        
        defect_rate = (total_defects / total_quantity) * per_units
        return round(defect_rate, 2)
    
    # ========== Private Helper Methods ==========
    
    def _notify_critical_defect(self, defect: Defect) -> None:
        """Send notification for critical defects"""
        # TODO: Integrate with notification service
        # For now, just a placeholder
        pass


