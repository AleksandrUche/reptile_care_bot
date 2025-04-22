from __future__ import annotations

from typing import ClassVar, Any

from sqlalchemy import (
    ForeignKey,
    Boolean,
    DateTime,
    BigInteger,
    func,
    Enum,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import Mapped, mapped_column, relationship, DeclarativeBase

from enums.enum_role import UserRole, SubscriptionType, UserRoleCompany
from .pets_models import CompanyOrm, GroupOrm

DBJSON = dict[Any, Any] | list[dict[Any, Any]]


class BaseTable(AsyncAttrs, DeclarativeBase):
    type_annotation_map: ClassVar[dict[Any, Any]] = {DBJSON: JSONB}


class UsersTable(BaseTable):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(
        BigInteger, unique=True, nullable=False, index=True
    )
    username: Mapped[str | None]
    first_name: Mapped[str | None]
    last_name: Mapped[str | None]
    role: Mapped[UserRole] = mapped_column(
        "Роль пользователя", Enum(UserRole), default=UserRole.USER
    )
    is_active: Mapped[bool] = mapped_column("Активный?", Boolean, default=True)
    tz_region: Mapped[str | None] = mapped_column("Регион")
    tz_offset: Mapped[int | None] = mapped_column("Часовой пояс")
    longitude: Mapped[float | None] = mapped_column("Долгота")
    latitude: Mapped[float | None] = mapped_column("Широта")
    language: Mapped[str | None]
    blocked: Mapped[bool] = mapped_column("Заблокирован?", Boolean, default=False)
    created_date = mapped_column(
        "Дата регистрации", DateTime(timezone=True), server_default=func.now()
    )
    companies: Mapped[list["CompanyOrm"]] = relationship(
        "CompanyOrm", back_populates="user"
    )
    shared_companies: Mapped[list["UserCompanyAssociationsTable"]] = relationship(
        "UserCompanyAssociation",
        back_populates="user",
    )
    shared_groups: Mapped[list["UserGroupAssociation"]] = relationship(
        "UserGroupAssociation", back_populates="user"
    )
    subscriptions: Mapped[list["UserSubscriptionsTable"]] = relationship(
        "UserSubscriptionTable", back_populates="user"
    )

    @property
    def full_name(self) -> str | None:
        name = str(self.first_name), str(self.last_name)
        return " ".join(name).replace("None", "").strip() or None


class SubscriptionsTable(BaseTable):
    __tablename__ = "subscription"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    subscription_type: Mapped[SubscriptionType] = mapped_column(
        "Тип подписки", Enum(SubscriptionType), default=SubscriptionType.ONE_MONTH
    )
    price: Mapped[int] = mapped_column("Цена")
    duration: Mapped[int] = mapped_column("Продолжительность")
    is_active: Mapped[bool] = mapped_column("Активная?", Boolean, default=True)


class UserSubscriptionsTable(BaseTable):
    __tablename__ = "user_subscriptions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    created_date = mapped_column(
        "Дата начала", DateTime(timezone=True), server_default=func.now()
    )
    expires_date: Mapped[DateTime] = mapped_column(
        "Дата окончания", DateTime(timezone=True), nullable=False
    )
    is_active: Mapped[bool] = mapped_column("Активная?", Boolean, default=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True)
    user: Mapped[UsersTable] = relationship(
        UsersTable, back_populates="subscription", uselist=False
    )

    subscription_id: Mapped[int] = mapped_column(ForeignKey("subscriptions.id"))
    subscription: Mapped[UserSubscriptionsTable] = relationship(back_populates="users")


class UserCompanyAssociationsTable(BaseTable):
    __tablename__ = "user_company_associations"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    role: Mapped[UserRoleCompany] = mapped_column(
        "Роль", Enum(UserRoleCompany), default=UserRoleCompany.VIEWER
    )

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped[UsersTable] = relationship(back_populates="shared_companies")

    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"))
    company: Mapped["CompanyOrm"] = relationship(
        "CompaniesTable", back_populates="shared_users"
    )  # TODO: ГДЕ ТО __tablename__ В ЕДИНСТВЕННОМ ЧИСЛЕ, ГДЕ ТО ВО МНОЖЕСТВЕННОМ

    __table_args__ = (
        UniqueConstraint("user_id", "company_id", name="uq_user_company"),
    )


class UserGroupAssociation(BaseTable):
    __tablename__ = "user_group_association"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    group_id: Mapped[int] = mapped_column(ForeignKey("group.id"))
    role: Mapped[UserRoleCompany] = mapped_column(
        "Роль", Enum(UserRoleCompany), default=UserRoleCompany.VIEWER
    )
    user: Mapped[UsersTable] = relationship("UserOrm", back_populates="shared_groups")
    group: Mapped[GroupOrm] = relationship("GroupOrm", back_populates="shared_users")

    __table_args__ = (UniqueConstraint("user_id", "group_id", name="uq_user_group"),)
