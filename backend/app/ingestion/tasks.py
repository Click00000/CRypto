"""
Celery tasks for ingestion
This file will be imported by worker
"""
import logging

logger = logging.getLogger(__name__)

# Tasks will be registered by celery_app in worker


def evm_sync_task():
    """EVM sync task"""
    from app.db.session import SessionLocal
    from app.ingestion.evm.sync import EVMSync
    
    db = SessionLocal()
    try:
        sync = EVMSync(db)
        result = sync.sync()
        logger.info(f"EVM sync completed: {result}")
        return result
    except Exception as e:
        logger.error(f"EVM sync failed: {e}")
        raise
    finally:
        db.close()


def btc_sync_task():
    """BTC sync task"""
    from app.db.session import SessionLocal
    from app.ingestion.btc.sync import BTCSync
    
    db = SessionLocal()
    try:
        sync = BTCSync(db)
        result = sync.sync()
        logger.info(f"BTC sync completed: {result}")
        return result
    except Exception as e:
        logger.error(f"BTC sync failed: {e}")
        raise
    finally:
        db.close()


def metrics_aggregate_task():
    """Metrics aggregation task"""
    from app.db.session import SessionLocal
    from app.services.metrics import MetricsService
    
    db = SessionLocal()
    try:
        service = MetricsService(db)
        result_1h = service.aggregate_metrics("1h")
        result_1d = service.aggregate_metrics("1d")
        logger.info(f"Metrics aggregation completed: 1h={result_1h}, 1d={result_1d}")
        return {"1h": result_1h, "1d": result_1d}
    except Exception as e:
        logger.error(f"Metrics aggregation failed: {e}")
        raise
    finally:
        db.close()


def alerts_task():
    """Alerts task"""
    from app.db.session import SessionLocal
    from app.services.metrics import AlertsService
    
    db = SessionLocal()
    try:
        service = AlertsService(db)
        result_1h = service.check_anomalies("1h")
        result_1d = service.check_anomalies("1d")
        logger.info(f"Alerts check completed: 1h={result_1h}, 1d={result_1d}")
        return {"1h": result_1h, "1d": result_1d}
    except Exception as e:
        logger.error(f"Alerts check failed: {e}")
        raise
    finally:
        db.close()
