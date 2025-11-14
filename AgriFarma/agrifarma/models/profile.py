# -*- coding: utf-8 -*-
from datetime import datetime, UTC
from agrifarma.extensions import db

PROFESSIONS = ("farmer", "academic", "consultant", "other")
EXPERTISE_LEVELS = ("expert", "intermediate", "beginner")

class Profile(db.Model):
    __tablename__ = "profiles"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, unique=True)

    name = db.Column(db.String(120), nullable=False)
    mobile = db.Column(db.String(20))
    city = db.Column(db.String(64))
    state = db.Column(db.String(64))
    country = db.Column(db.String(64))

    profession = db.Column(db.String(32))  # one of PROFESSIONS
    expertise_level = db.Column(db.String(32))  # one of EXPERTISE_LEVELS

    profile_picture = db.Column(db.String(256))  # Legacy field
    display_picture = db.Column(db.String(256))  # Filename for uploaded DP
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))

    user = db.relationship("User", back_populates="profile")

    # Activity metrics derived from forum and likes
    @property
    def posts_count(self) -> int:
        from agrifarma.models.forum import Post
        return db.session.query(Post).filter_by(author_id=self.user_id).count()

    @property
    def likes_count(self) -> int:
        from agrifarma.models.forum import Post as ForumPost
        from agrifarma.models.likes import PostLike
        # Count likes on posts authored by this user
        return (
            db.session.query(PostLike)
            .join(ForumPost, ForumPost.id == PostLike.post_id)
            .filter(ForumPost.author_id == self.user_id)
            .count()
        )

    @property
    def latest_posts(self) -> list:
        from agrifarma.models.forum import Post
        return (
            db.session.query(Post)
            .filter_by(author_id=self.user_id)
            .order_by(Post.created_at.desc())
            .limit(5)
            .all()
        )
