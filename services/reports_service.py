import logging
import json
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, desc

from models import SalesReport
from models import Order, OrderItem, Product, Category

logger = logging.getLogger(__name__)


class ReportsService:
    def __init__(self, db: Session):
        self.db = db
    
    def generate_report(self, period: str, start_date: Optional[date] = None, end_date: Optional[date] = None) -> SalesReport:
        """Generate a sales report for the specified period"""
        try:
            # Calculate date range if not provided
            if not start_date or not end_date:
                start_date, end_date = self._calculate_period_dates(period)
            
            # Check if report already exists for this period
            existing_report = self.db.query(SalesReport).filter(
                and_(
                    SalesReport.period == period,
                    SalesReport.start_date == start_date,
                    SalesReport.end_date == end_date
                )
            ).first()
            
            if existing_report:
                logger.info(f"Report for {period} {start_date} to {end_date} already exists, updating...")
                # Update existing report
                existing_report.totals_json = self._generate_report_data(start_date, end_date)
                existing_report.generated_at = datetime.utcnow()
                self.db.commit()
                self.db.refresh(existing_report)
                return existing_report
            
            # Generate new report
            report_data = self._generate_report_data(start_date, end_date)
            
            report = SalesReport(
                period=period,
                start_date=start_date,
                end_date=end_date,
                totals_json=report_data
            )
            
            self.db.add(report)
            self.db.commit()
            self.db.refresh(report)
            
            logger.info(f"Generated {period} report for {start_date} to {end_date}")
            return report
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error generating {period} report: {e}")
            raise
    
    def _calculate_period_dates(self, period: str) -> tuple[date, date]:
        """Calculate start and end dates for the specified period"""
        today = date.today()
        
        if period == "weekly":
            # Find last Monday
            days_since_monday = today.weekday()
            start_date = today - timedelta(days=days_since_monday)
            end_date = start_date + timedelta(days=6)
        elif period == "monthly":
            # Previous month
            if today.month == 1:
                start_date = date(today.year - 1, 12, 1)
                end_date = date(today.year - 1, 12, 31)
            else:
                start_date = date(today.year, today.month - 1, 1)
                # Last day of previous month
                if today.month == 1:
                    end_date = date(today.year - 1, 12, 31)
                else:
                    end_date = date(today.year, today.month, 1) - timedelta(days=1)
        else:
            raise ValueError(f"Invalid period: {period}. Must be 'weekly' or 'monthly'")
        
        return start_date, end_date
    
    def _generate_report_data(self, start_date: date, end_date: date) -> str:
        """Generate the actual report data"""
        try:
            # Convert dates to datetime for database query
            start_datetime = datetime.combine(start_date, datetime.min.time())
            end_datetime = datetime.combine(end_date, datetime.max.time())
            
            # Get orders in the period
            orders = self.db.query(Order).filter(
                and_(
                    Order.created_at >= start_datetime,
                    Order.created_at <= end_datetime,
                    Order.status.in_(['approved', 'sold'])
                )
            ).all()
            
            # Calculate basic metrics
            total_orders = len(orders)
            total_revenue = sum(order.final_amount for order in orders)
            avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
            
            # Get top products by quantity
            top_products = self.db.query(
                Product.name,
                Product.code,
                func.sum(OrderItem.quantity).label('total_quantity'),
                func.sum(OrderItem.quantity * OrderItem.unit_price).label('total_revenue')
            ).join(OrderItem, Product.id == OrderItem.product_id).join(
                Order, OrderItem.order_id == Order.id
            ).filter(
                and_(
                    Order.created_at >= start_datetime,
                    Order.created_at <= end_datetime,
                    Order.status.in_(['approved', 'sold'])
                )
            ).group_by(Product.id, Product.name, Product.code).order_by(
                desc(func.sum(OrderItem.quantity))
            ).limit(10).all()
            
            # Get top categories by revenue
            top_categories = self.db.query(
                Category.name,
                func.sum(OrderItem.quantity * OrderItem.unit_price).label('total_revenue'),
                func.sum(OrderItem.quantity).label('total_quantity')
            ).join(Product, Category.id == Product.category_id).join(
                OrderItem, Product.id == OrderItem.product_id
            ).join(Order, OrderItem.order_id == Order.id).filter(
                and_(
                    Order.created_at >= start_datetime,
                    Order.created_at <= end_datetime,
                    Order.status.in_(['approved', 'sold'])
                )
            ).group_by(Category.id, Category.name).order_by(
                desc(func.sum(OrderItem.quantity * OrderItem.unit_price))
            ).limit(10).all()
            
            # Get low stock alerts
            low_stock_products = self.db.query(Product).filter(
                and_(
                    Product.stock <= Product.low_stock_threshold,
                    Product.is_active == True
                )
            ).all()
            
            # Compile report data
            report_data = {
                'orders': {
                    'total': total_orders,
                    'revenue': total_revenue,
                    'avg_order_value': avg_order_value
                },
                'top_products': [
                    {
                        'name': product.name,
                        'code': product.code,
                        'quantity': int(product.total_quantity),
                        'revenue': float(product.total_revenue)
                    }
                    for product in top_products
                ],
                'top_categories': [
                    {
                        'name': category.name,
                        'revenue': float(category.total_revenue),
                        'quantity': int(category.total_quantity)
                    }
                    for category in top_categories
                ],
                'low_stock_alerts': [
                    {
                        'name': product.name,
                        'code': product.code,
                        'current_stock': product.stock,
                        'threshold': product.low_stock_threshold
                    }
                    for product in low_stock_products
                ],
                'period_summary': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat(),
                    'days': (end_date - start_date).days + 1
                }
            }
            
            return json.dumps(report_data, ensure_ascii=False, indent=2)
            
        except Exception as e:
            logger.error(f"Error generating report data: {e}")
            return json.dumps({'error': str(e)})
    
    def get_latest_report(self, period: str) -> Optional[SalesReport]:
        """Get the latest report for the specified period"""
        try:
            report = self.db.query(SalesReport).filter(
                SalesReport.period == period
            ).order_by(desc(SalesReport.generated_at)).first()
            
            return report
            
        except Exception as e:
            logger.error(f"Error getting latest {period} report: {e}")
            return None
    
    def list_reports(self, period: Optional[str] = None, limit: int = 20) -> List[SalesReport]:
        """List recent reports with optional period filtering"""
        try:
            query = self.db.query(SalesReport)
            
            if period:
                query = query.filter(SalesReport.period == period)
            
            reports = query.order_by(desc(SalesReport.generated_at)).limit(limit).all()
            
            return reports
            
        except Exception as e:
            logger.error(f"Error listing reports: {e}")
            return []
    
    def get_report_summary(self, report_id: int) -> Optional[Dict[str, Any]]:
        """Get a formatted summary of a report"""
        try:
            report = self.db.query(SalesReport).filter(SalesReport.id == report_id).first()
            if not report:
                return None
            
            # Parse the JSON data
            try:
                data = json.loads(report.totals_json)
            except json.JSONDecodeError:
                logger.error(f"Invalid JSON in report {report_id}")
                return None
            
            # Format the summary
            summary = {
                'id': report.id,
                'period': report.period,
                'start_date': report.start_date,
                'end_date': report.end_date,
                'generated_at': report.generated_at,
                'total_orders': data.get('orders', {}).get('total', 0),
                'total_revenue': data.get('orders', {}).get('revenue', 0),
                'avg_order_value': data.get('orders', {}).get('avg_order_value', 0),
                'top_products_count': len(data.get('top_products', [])),
                'top_categories_count': len(data.get('top_categories', [])),
                'low_stock_alerts_count': len(data.get('low_stock_alerts', []))
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Error getting report summary for {report_id}: {e}")
            return None
    
    def generate_csv(self, report_id: int) -> Optional[str]:
        """Generate CSV content for a report"""
        try:
            report = self.db.query(SalesReport).filter(SalesReport.id == report_id).first()
            if not report:
                return None
            
            # Parse the JSON data
            try:
                data = json.loads(report.totals_json)
            except json.JSONDecodeError:
                logger.error(f"Invalid JSON in report {report_id}")
                return None
            
            # Generate CSV content
            csv_lines = []
            
            # Header
            csv_lines.append("Sales Report")
            csv_lines.append(f"Period: {report.period}")
            csv_lines.append(f"Date Range: {report.start_date} to {report.end_date}")
            csv_lines.append(f"Generated: {report.generated_at}")
            csv_lines.append("")
            
            # Orders summary
            csv_lines.append("Orders Summary")
            csv_lines.append("Total Orders,Total Revenue,Average Order Value")
            orders = data.get('orders', {})
            csv_lines.append(f"{orders.get('total', 0)},{orders.get('revenue', 0):.2f},{orders.get('avg_order_value', 0):.2f}")
            csv_lines.append("")
            
            # Top products
            csv_lines.append("Top Products by Quantity")
            csv_lines.append("Rank,Product Name,Code,Quantity,Revenue")
            for i, product in enumerate(data.get('top_products', [])[:10], 1):
                csv_lines.append(f"{i},{product.get('name', '')},{product.get('code', '')},{product.get('quantity', 0)},{product.get('revenue', 0):.2f}")
            csv_lines.append("")
            
            # Top categories
            csv_lines.append("Top Categories by Revenue")
            csv_lines.append("Rank,Category Name,Revenue,Quantity")
            for i, category in enumerate(data.get('top_categories', [])[:10], 1):
                csv_lines.append(f"{i},{category.get('name', '')},{category.get('revenue', 0):.2f},{category.get('quantity', 0)}")
            csv_lines.append("")
            
            # Low stock alerts
            csv_lines.append("Low Stock Alerts")
            csv_lines.append("Product Name,Code,Current Stock,Threshold")
            for alert in data.get('low_stock_alerts', []):
                csv_lines.append(f"{alert.get('name', '')},{alert.get('code', '')},{alert.get('current_stock', 0)},{alert.get('threshold', 0)}")
            
            return "\n".join(csv_lines)
            
        except Exception as e:
            logger.error(f"Error generating CSV for report {report_id}: {e}")
            return None
    
    def cleanup_old_reports(self, days: int = 90) -> int:
        """Clean up reports older than specified days"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            old_reports = self.db.query(SalesReport).filter(
                SalesReport.generated_at < cutoff_date
            ).all()
            
            count = len(old_reports)
            for report in old_reports:
                self.db.delete(report)
            
            self.db.commit()
            
            logger.info(f"Cleaned up {count} old reports older than {days} days")
            return count
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error cleaning up old reports: {e}")
            return 0 