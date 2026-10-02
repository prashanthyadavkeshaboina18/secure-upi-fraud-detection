"""initial schema: users, transactions, fraud_alerts, model_logs

Revision ID: 0001
Revises:
Create Date: 2026-09-17
"""
from alembic import op
import sqlalchemy as sa

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None

user_role = sa.Enum("USER", "ADMIN", name="userrole")
risk_level = sa.Enum("LOW", "MEDIUM", "HIGH", name="risklevel")
decision = sa.Enum("APPROVED", "REVIEW", "BLOCKED", "CANCELLED", name="decision")
alert_severity = sa.Enum("LOW", "MEDIUM", "HIGH", name="alertseverity")
alert_status = sa.Enum("NEW", "REVIEWED", "DISMISSED", name="alertstatus")


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("email", sa.String(150), nullable=False, unique=True),
        sa.Column("phone", sa.String(15), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("role", user_role, nullable=False, server_default="USER"),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    )
    op.create_index("idx_users_email", "users", ["email"])

    op.create_table(
        "transactions",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("transaction_id", sa.String(40), nullable=False, unique=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("receiver_vpa", sa.String(100), nullable=False),
        sa.Column("merchant_name", sa.String(120), nullable=True),
        sa.Column("merchant_category", sa.String(60), nullable=False),
        sa.Column("transaction_type", sa.String(20), nullable=False),
        sa.Column("device_id", sa.String(100), nullable=False),
        sa.Column("device_type", sa.String(20), nullable=False),
        sa.Column("location_city", sa.String(60), nullable=False),
        sa.Column("fraud_probability", sa.Float, nullable=True),
        sa.Column("risk_score", sa.Integer, nullable=True),
        sa.Column("risk_level", risk_level, nullable=True),
        sa.Column("decision", decision, nullable=False),
        sa.Column("reasons", sa.JSON, nullable=True),
        sa.Column("model_version", sa.String(40), nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("confirmed_at", sa.DateTime, nullable=True),
    )
    op.create_index("idx_txn_user_time", "transactions", ["user_id", "created_at"])
    op.create_index("idx_txn_risk", "transactions", ["risk_level"])
    op.create_index("idx_txn_decision", "transactions", ["decision"])
    op.create_index("idx_txn_created", "transactions", ["created_at"])
    op.create_index("ix_transactions_transaction_id", "transactions", ["transaction_id"])

    op.create_table(
        "fraud_alerts",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("transaction_id", sa.Integer, sa.ForeignKey("transactions.id"), nullable=False),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("alert_type", sa.String(60), nullable=False),
        sa.Column("message", sa.Text, nullable=False),
        sa.Column("severity", alert_severity, nullable=False),
        sa.Column("status", alert_status, nullable=False, server_default="NEW"),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("reviewed_at", sa.DateTime, nullable=True),
    )
    op.create_index("idx_alert_status", "fraud_alerts", ["status"])

    op.create_table(
        "model_logs",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("transaction_id", sa.Integer, sa.ForeignKey("transactions.id"), nullable=False),
        sa.Column("model_name", sa.String(60), nullable=False),
        sa.Column("model_version", sa.String(40), nullable=False),
        sa.Column("prediction", sa.Integer, nullable=False),
        sa.Column("probability", sa.Float, nullable=False),
        sa.Column("latency_ms", sa.Integer, nullable=False),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("model_logs")
    op.drop_index("idx_alert_status", table_name="fraud_alerts")
    op.drop_table("fraud_alerts")
    op.drop_index("ix_transactions_transaction_id", table_name="transactions")
    op.drop_index("idx_txn_created", table_name="transactions")
    op.drop_index("idx_txn_decision", table_name="transactions")
    op.drop_index("idx_txn_risk", table_name="transactions")
    op.drop_index("idx_txn_user_time", table_name="transactions")
    op.drop_table("transactions")
    op.drop_index("idx_users_email", table_name="users")
    op.drop_table("users")
    decision.drop(op.get_bind(), checkfirst=True)
    risk_level.drop(op.get_bind(), checkfirst=True)
    alert_status.drop(op.get_bind(), checkfirst=True)
    alert_severity.drop(op.get_bind(), checkfirst=True)
    user_role.drop(op.get_bind(), checkfirst=True)
