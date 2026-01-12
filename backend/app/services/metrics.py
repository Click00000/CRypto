from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from app.db.models import RawTransfer, FlowMetric, Exchange
from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class MetricsService:
    """Metrics aggregation service"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def aggregate_metrics(self, window: str = "1h") -> Dict[str, Any]:
        """Aggregate flow metrics from raw transfers"""
        # Determine time bucket function based on window
        if window == "1h":
            time_bucket_expr = func.date_trunc("hour", RawTransfer.timestamp)
        elif window == "1d":
            time_bucket_expr = func.date_trunc("day", RawTransfer.timestamp)
        else:
            raise ValueError(f"Unsupported window: {window}")
        
        # Get all transfers
        transfers = self.db.query(RawTransfer).all()
        
        # Group by time_bucket, exchange, asset
        metrics_map = {}
        
        for transfer in transfers:
            time_bucket = self._get_time_bucket(transfer.timestamp, window)
            key = (
                time_bucket.isoformat(),
                str(transfer.exchange_to_id) if transfer.exchange_to_id else None,
                str(transfer.exchange_from_id) if transfer.exchange_from_id else None,
                transfer.asset_symbol
            )
            
            if key not in metrics_map:
                metrics_map[key] = {
                    "time_bucket": time_bucket,
                    "window": window,
                    "exchange_id": transfer.exchange_to_id or transfer.exchange_from_id,
                    "asset_symbol": transfer.asset_symbol,
                    "inflow": Decimal(0),
                    "outflow": Decimal(0),
                    "netflow": Decimal(0)
                }
            
            metric = metrics_map[key]
            
            if transfer.direction == "deposit":
                metric["inflow"] += transfer.amount
                metric["netflow"] += transfer.amount
            elif transfer.direction == "withdraw":
                metric["outflow"] += transfer.amount
                metric["netflow"] -= transfer.amount
        
        # Upsert metrics
        created_count = 0
        updated_count = 0
        
        for key, metric_data in metrics_map.items():
            existing = self.db.query(FlowMetric).filter(
                FlowMetric.time_bucket == metric_data["time_bucket"],
                FlowMetric.window == window,
                FlowMetric.exchange_id == metric_data["exchange_id"],
                FlowMetric.asset_symbol == metric_data["asset_symbol"]
            ).first()
            
            if existing:
                existing.inflow = metric_data["inflow"]
                existing.outflow = metric_data["outflow"]
                existing.netflow = metric_data["netflow"]
                existing.updated_at = datetime.utcnow()
                updated_count += 1
            else:
                new_metric = FlowMetric(**metric_data)
                self.db.add(new_metric)
                created_count += 1
        
        self.db.commit()
        
        return {
            "created": created_count,
            "updated": updated_count,
            "total": len(metrics_map)
        }
    
    def _get_time_bucket(self, dt: datetime, window: str) -> datetime:
        """Get time bucket for a datetime"""
        if window == "1h":
            return dt.replace(minute=0, second=0, microsecond=0)
        elif window == "1d":
            return dt.replace(hour=0, minute=0, second=0, microsecond=0)
        else:
            return dt


class AlertsService:
    """Alerts service for anomaly detection"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def check_anomalies(self, window: str = "1h", baseline_days: int = 30) -> Dict[str, Any]:
        """Check for anomalies using z-score"""
        from app.db.models import Alert
        
        # Get recent metrics
        cutoff = datetime.utcnow() - timedelta(days=baseline_days)
        recent_metrics = self.db.query(FlowMetric).filter(
            FlowMetric.window == window,
            FlowMetric.time_bucket >= cutoff
        ).all()
        
        # Group by exchange + asset
        grouped = {}
        for metric in recent_metrics:
            key = (metric.exchange_id, metric.asset_symbol)
            if key not in grouped:
                grouped[key] = []
            grouped[key].append(metric)
        
        alerts_created = 0
        
        for (exchange_id, asset_symbol), metrics in grouped.items():
            if len(metrics) < 2:
                continue  # Need at least 2 data points
            
            # Sort by time
            metrics_sorted = sorted(metrics, key=lambda m: m.time_bucket)
            
            # Calculate baseline (mean and std from historical data, excluding most recent)
            historical = metrics_sorted[:-1]
            if len(historical) < 2:
                continue
            
            netflows = [float(m.netflow) for m in historical]
            mean = sum(netflows) / len(netflows)
            variance = sum((x - mean) ** 2 for x in netflows) / len(netflows)
            std = variance ** 0.5 if variance > 0 else 1
            
            # Check most recent metric
            latest = metrics_sorted[-1]
            z_score = (float(latest.netflow) - mean) / std if std > 0 else 0
            
            # Alert if |z| >= 3
            if abs(z_score) >= 3:
                # Check if alert already exists for this time_bucket
                existing = self.db.query(Alert).filter(
                    Alert.exchange_id == exchange_id,
                    Alert.asset_symbol == asset_symbol,
                    Alert.window == window,
                    Alert.created_at >= latest.time_bucket,
                    Alert.created_at < latest.time_bucket + timedelta(hours=1 if window == "1h" else 24)
                ).first()
                
                if not existing:
                    alert = Alert(
                        exchange_id=exchange_id,
                        asset_symbol=asset_symbol,
                        window=window,
                        z_score=Decimal(str(z_score)),
                        netflow=latest.netflow,
                        baseline_mean=Decimal(str(mean)),
                        baseline_std=Decimal(str(std))
                    )
                    self.db.add(alert)
                    alerts_created += 1
        
        self.db.commit()
        
        return {
            "alerts_created": alerts_created,
            "groups_checked": len(grouped)
        }
