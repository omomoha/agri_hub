from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from app.core.database import get_session
from app.models.user import User
from datetime import datetime

router = APIRouter()

@router.get("/health")
async def health_check(session: Session = Depends(get_session)):
    """
    Health check endpoint for monitoring and load balancers.
    Returns the health status of the application and database.
    """
    try:
        # Check database connectivity
        db_healthy = False
        try:
            # Simple query to test database connection
            result = session.exec(select(User).limit(1))
            db_healthy = True
        except Exception:
            db_healthy = False
        
        # Determine overall health
        overall_healthy = db_healthy
        
        health_status = {
            "status": "healthy" if overall_healthy else "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0",
            "services": {
                "api": "healthy",
                "database": "healthy" if db_healthy else "unhealthy"
            }
        }
        
        status_code = 200 if overall_healthy else 503
        return health_status, status_code
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0",
            "error": str(e),
            "services": {
                "api": "unhealthy",
                "database": "unknown"
            }
        }, 503

@router.get("/health/ready")
async def readiness_check(session: Session = Depends(get_session)):
    """
    Readiness check endpoint for Kubernetes readiness probes.
    Checks if the application is ready to receive traffic.
    """
    try:
        # Check database connectivity
        db_ready = False
        try:
            # Simple query to test database connection
            result = session.exec(select(User).limit(1))
            db_ready = True
        except Exception:
            db_ready = False
        
        # Application is ready if database is accessible
        ready = db_ready
        
        readiness_status = {
            "ready": ready,
            "timestamp": datetime.utcnow().isoformat(),
            "checks": {
                "database": "ready" if db_ready else "not_ready"
            }
        }
        
        status_code = 200 if ready else 503
        return readiness_status, status_code
        
    except Exception as e:
        return {
            "ready": False,
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e),
            "checks": {
                "database": "unknown"
            }
        }, 503

@router.get("/health/live")
async def liveness_check():
    """
    Liveness check endpoint for Kubernetes liveness probes.
    Simple check to see if the application is running.
    """
    return {
        "alive": True,
        "timestamp": datetime.utcnow().isoformat()
    }
