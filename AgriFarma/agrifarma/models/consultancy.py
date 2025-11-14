# -*- coding: utf-8 -*-
from datetime import datetime, UTC
from agrifarma.extensions import db
from .user import User
from .profile import EXPERTISE_LEVELS

CONSULTANT_CATEGORIES = (
    "soil",
    "irrigation",
    "crop_disease",
    "fertilizers",
    "market",
    "other",
)

APPROVAL_STATUSES = (
    "Pending",
    "Approved",
    "Rejected",
)


class Consultant(db.Model):
    __tablename__ = "consultants"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)

    category = db.Column(db.String(64), nullable=False)  # one of CONSULTANT_CATEGORIES
    expertise_level = db.Column(db.String(32), nullable=False)  # one of EXPERTISE_LEVELS
    contact_email = db.Column(db.String(120), nullable=False)
    approval_status = db.Column(db.String(16), default="Pending", index=True)  # Pending/Approved/Rejected

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))

    user = db.relationship("User")

    def is_approved(self) -> bool:
        return self.approval_status == "Approved"

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Consultant user={self.user_id} category={self.category} status={self.approval_status}>"
