"""
RefreshToken Repository - Data access layer for RefreshToken entity.
"""

from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from src.domain.models import RefreshToken


class RefreshTokenRepository:
    """Repository for RefreshToken entity operations."""

    def __init__(self, db: Session):
        """
        Initialize repository with database session.

        Args:
            db: SQLAlchemy database session
        """
        self.db = db

    def create(self, user_id: UUID, token_hash: str, expires_at: datetime) -> RefreshToken:
        """
        Persist a new refresh token.

        Args:
            user_id: Owner user UUID
            token_hash: SHA-256 hex digest of the raw token
            expires_at: Token expiration datetime (UTC)

        Returns:
            RefreshToken: Created instance
        """
        token = RefreshToken(
            user_id=user_id,
            token_hash=token_hash,
            expires_at=expires_at,
            is_revoked=False,
        )
        self.db.add(token)
        self.db.commit()
        self.db.refresh(token)
        return token

    def get_by_hash(self, token_hash: str) -> Optional[RefreshToken]:
        """
        Look up a refresh token by its SHA-256 hash.

        Args:
            token_hash: 64-char hex digest

        Returns:
            Optional[RefreshToken]: Token instance or None
        """
        return self.db.query(RefreshToken).filter(RefreshToken.token_hash == token_hash).first()

    def revoke(self, token: RefreshToken) -> None:
        """
        Mark a single refresh token as revoked.

        Args:
            token: RefreshToken instance to revoke
        """
        token.is_revoked = True
        self.db.commit()

    def revoke_all_for_user(self, user_id: UUID) -> int:
        """
        Revoke every active refresh token for a user.

        This is called on reuse detection (a revoked token was presented)
        to invalidate all sessions and force re-login.

        Args:
            user_id: User UUID

        Returns:
            int: Number of tokens revoked
        """
        tokens: List[RefreshToken] = (
            self.db.query(RefreshToken)
            .filter(
                RefreshToken.user_id == str(user_id),
                RefreshToken.is_revoked.is_(False),
            )
            .all()
        )
        for t in tokens:
            t.is_revoked = True
        self.db.commit()
        return len(tokens)

    def delete_expired(self, user_id: UUID) -> int:
        """
        Hard-delete expired tokens for a user to keep the table lean.

        Args:
            user_id: User UUID

        Returns:
            int: Number of rows deleted
        """
        now = datetime.now(timezone.utc)
        rows = (
            self.db.query(RefreshToken)
            .filter(
                RefreshToken.user_id == str(user_id),
                RefreshToken.expires_at < now,
            )
            .all()
        )
        for r in rows:
            self.db.delete(r)
        self.db.commit()
        return len(rows)
