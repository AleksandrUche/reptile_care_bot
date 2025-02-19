from __future__ import annotations

from sqlalchemy import ForeignKey, Boolean, DateTime, BigInteger, func, Enum, \
    UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.engine import Base
from enums.enum_role import UserRole, SubscriptionType, UserRoleCompany
from .pets_models import CompanyOrm, GroupOrm


class UserOrm(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False,
                                             index=True)
    username: Mapped[str] = mapped_column(nullable=True)
    first_name: Mapped[str] = mapped_column(nullable=True)
    last_name: Mapped[str] = mapped_column(nullable=True)
    role: Mapped[UserRole] = mapped_column(
        'Роль пользователя', Enum(UserRole), default=UserRole.USER
    )
    is_active: Mapped[bool] = mapped_column('Активный?', Boolean, default=True)
    blocked: Mapped[bool] = mapped_column('Заблокирован?', Boolean, default=False)
    created_date = mapped_column(
        'Дата регистрации', DateTime(timezone=True), server_default=func.now()
    )
    companies: Mapped[list['CompanyOrm']] = relationship(
        'CompanyOrm', back_populates='user'
    )
    shared_companies: Mapped[list['UserCompanyAssociation']] = relationship(
        'UserCompanyAssociation', back_populates='user'
    )
    shared_groups: Mapped[list['UserGroupAssociation']] = relationship(
        'UserGroupAssociation', back_populates='user'
    )
    subscriptions: Mapped[list['UserSubscriptionOrm']] = relationship(
        'UserSubscriptionOrm', back_populates='users'
    )

    @property
    def full_name(self):
        parts = []
        if self.first_name:
            parts.append(self.first_name)
        if self.last_name:
            parts.append(self.last_name)
        return ' '.join(parts) if parts else None


class UserSubscriptionOrm(Base):
    __tablename__ = 'user_subscriptions'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    created_date = mapped_column(
        'Дата начала', DateTime(timezone=True), server_default=func.now()
    )
    expires_date: Mapped[DateTime] = mapped_column(
        'Дата окончания', DateTime(timezone=True), nullable=False
    )
    is_active: Mapped[bool] = mapped_column('Активная?', Boolean, default=True)
    users: Mapped['UserOrm'] = relationship('UserOrm', back_populates='subscriptions')
    subscriptions: Mapped[list['SubscriptionOrm']] = relationship(
        'SubscriptionOrm', back_populates='user_subscription'
    )


class SubscriptionOrm(Base):
    __tablename__ = 'subscription'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    subscription_type: Mapped[SubscriptionType] = mapped_column(
        'Тип подписки', Enum(SubscriptionType), default=SubscriptionType.ONE_MONTH)
    price: Mapped[int] = mapped_column('Цена', nullable=False)
    duration: Mapped[int] = mapped_column('Продолжительность', nullable=False)
    is_active: Mapped[bool] = mapped_column('Активная?', Boolean, default=True)
    user_subscription_id: Mapped[int] = mapped_column(ForeignKey('user_subscriptions.id'))
    user_subscription: Mapped['UserSubscriptionOrm'] = relationship(
        'UserSubscriptionOrm', back_populates='subscriptions'
    )


class UserCompanyAssociation(Base):
    __tablename__ = 'user_company_association'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    company_id: Mapped[int] = mapped_column(ForeignKey('company.id'))
    role: Mapped[UserRoleCompany] = mapped_column(
        'Роль', Enum(UserRoleCompany), default=UserRoleCompany.VIEWER
    )
    user: Mapped['UserOrm'] = relationship('UserOrm', back_populates='shared_companies')
    company: Mapped['CompanyOrm'] = relationship(
        'CompanyOrm', back_populates='shared_users'
    )

    __table_args__ = (
        UniqueConstraint('user_id', 'company_id', name='uq_user_company'),
    )


class UserGroupAssociation(Base):
    __tablename__ = 'user_group_association'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    group_id: Mapped[int] = mapped_column(ForeignKey('group.id'))
    role: Mapped[UserRoleCompany] = mapped_column('Роль', Enum(UserRoleCompany),
                                                  default=UserRoleCompany.VIEWER)
    user: Mapped['UserOrm'] = relationship('UserOrm', back_populates='shared_groups')
    group: Mapped['GroupOrm'] = relationship('GroupOrm', back_populates='shared_users')

    __table_args__ = (
        UniqueConstraint('user_id', 'group_id', name='uq_user_group'),
    )