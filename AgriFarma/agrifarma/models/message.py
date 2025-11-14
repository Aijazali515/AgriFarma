from datetime import datetime
from agrifarma.extensions import db

class Message(db.Model):
    __tablename__ = 'message'

    id = db.Column(db.Integer, primary_key=True)
    # Correct foreign key references to the users table (was mistakenly 'user.id')
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    subject = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    read = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships back to User model
    sender = db.relationship('User', foreign_keys=[sender_id], backref='sent_messages')
    receiver = db.relationship('User', foreign_keys=[receiver_id], backref='received_messages')

    def mark_as_read(self):
        """Mark message as read and persist the change."""
        self.read = True
        db.session.commit()

    def __repr__(self):  # pragma: no cover - debug helper
        return f'<Message {self.id} from User {self.sender_id} to User {self.receiver_id}>'
