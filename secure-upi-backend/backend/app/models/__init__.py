# Import every model here so Base.metadata knows about all tables when
# scripts call Base.metadata.create_all(), and so Alembic's autogenerate
# can see them.
from app.models.user import User, UserRole                      # noqa: F401
from app.models.transaction import Transaction, RiskLevel, Decision  # noqa: F401
from app.models.fraud_alert import FraudAlert, AlertSeverity, AlertStatus  # noqa: F401
from app.models.model_log import ModelLog                        # noqa: F401
