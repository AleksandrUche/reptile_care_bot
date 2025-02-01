from __future__ import annotations

from sqlalchemy import ForeignKey, Boolean, DateTime, BigInteger, func, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.engine import Base
from enums.enum_role import UserRole, SubscriptionType


class UserOrm(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    username: Mapped[str] = mapped_column(nullable=True)
    first_name: Mapped[str] = mapped_column(nullable=True)
    last_name: Mapped[str] = mapped_column(nullable=True)
    role: Mapped[UserRole] = mapped_column(
        'Роль пользователя', Enum(UserRole), default=UserRole.BASE
    )
    is_active: Mapped[bool] = mapped_column('Активный?', Boolean, default=True)
    created_date = mapped_column(
        'Дата регистрации', DateTime(timezone=True), server_default=func.now()
    )
    subscription_id: Mapped[int] = mapped_column(
        ForeignKey("subscriptions.id"), nullable=True
    )

    subscription: Mapped["SubscriptionOrm"] = relationship(
        "SubscriptionOrm", back_populates="users"
    )

    @property
    def full_name(self):
        parts = []
        if self.first_name:
            parts.append(self.first_name)
        if self.last_name:
            parts.append(self.last_name)
        return ' '.join(parts) if parts else None


class SubscriptionOrm(Base):
    __tablename__ = "subscriptions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    subscription_type: Mapped[SubscriptionType] = mapped_column(
        'Тип подписки', Enum(SubscriptionType), default=SubscriptionType.ONE_MONTH)
    price: Mapped[int] = mapped_column(nullable=False)
    created_date = mapped_column(
        'Дата начала', DateTime(timezone=True), server_default=func.now()
    )
    expires_date = mapped_column(
        'Дата окончания', DateTime(timezone=True), nullable=False
    )
    updated_date = mapped_column(
        'Дата обновления',
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    users: Mapped[list["UserOrm"]] = relationship("UserOrm", back_populates="subscription")
