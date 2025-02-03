from __future__ import annotations

from sqlalchemy import ForeignKey, DateTime, func, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.engine import Base
from enums.pets_enum import GenderRole


class CompanyOrm(Base):
    __tablename__ = 'company'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column('Название компании', nullable=False)
    description: Mapped[str] = mapped_column('Описание', nullable=True)
    updated_date = mapped_column(
        'Дата обновления',
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False,
                                         index=True)
    groups: Mapped[list['GroupOrm']] = relationship('GroupOrm',
                                                    back_populates='company')
    shared_users: Mapped[list['UserCompanyAssociation']] = relationship(
        'UserCompanyAssociation', back_populates='company')


class GroupOrm(Base):
    __tablename__ = 'group'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column('Название группы', nullable=False)
    description: Mapped[str] = mapped_column('Описание', nullable=True)
    updated_date = mapped_column(
        'Дата обновления',
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    company_id: Mapped[int] = mapped_column(
        ForeignKey('company.id'), unique=True, nullable=False
    )
    company: Mapped['CompanyOrm'] = relationship(
        'CompanyOrm', back_populates='groups'
    )

    pets: Mapped[list['PetOrm']] = relationship('PetOrm', back_populates='group')
    shared_users: Mapped[list['UserGroupAssociation']] = relationship(
        'UserGroupAssociation', back_populates='group')


class PetOrm(Base):
    __tablename__ = 'pet'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column('Имя', nullable=False)
    date_birth: Mapped[DateTime] = mapped_column('Дата рождения',
                                                 DateTime(timezone=True),
                                                 nullable=False)
    date_purchase: Mapped[DateTime] = mapped_column('Дата приобретения',
                                                    DateTime(timezone=True),
                                                    nullable=False)
    gender: Mapped[GenderRole] = mapped_column('Пол', Enum(GenderRole),
                                               default=GenderRole.NOT_DEFINED)
    morph: Mapped[str] = mapped_column('Морфа', nullable=True)
    view: Mapped[str] = mapped_column('Вид', nullable=True)
    photo: Mapped[str] = mapped_column('Фото', nullable=True)
    updated_date = mapped_column(
        'Дата обновления',
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )
    group_id: Mapped[int] = mapped_column(ForeignKey('group.id'), nullable=False)
    group: Mapped['GroupOrm'] = relationship('GroupOrm', back_populates='pets')

    weights: Mapped[list['WeightPetOrm']] = relationship('WeightPetOrm',
                                                         back_populates='pet')
    lengths: Mapped[list['LengthPetOrm']] = relationship('LengthPetOrm',
                                                         back_populates='pet')
    molting: Mapped[list['MoltingPetOrm']] = relationship('MoltingPetOrm',
                                                          back_populates='pet')


class WeightPetOrm(Base):
    __tablename__ = 'weight_pet'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    weight: Mapped[float] = mapped_column('Вес', nullable=False)
    description: Mapped[str] = mapped_column(nullable=True)
    pet_id: Mapped[int] = mapped_column(ForeignKey('pet.id'), nullable=False)
    date_measure: Mapped[DateTime] = mapped_column(
        'Дата взвешивания', DateTime(timezone=True), nullable=False
    )
    date: Mapped[DateTime] = mapped_column(
        'Дата обновления', DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    pet: Mapped['PetOrm'] = relationship('PetOrm', back_populates='weights')


class LengthPetOrm(Base):
    __tablename__ = 'length_pet'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    length: Mapped[float] = mapped_column('Длина', nullable=False)
    description: Mapped[str] = mapped_column(nullable=True)
    pet_id: Mapped[int] = mapped_column(ForeignKey('pet.id'), nullable=False)
    date_measure: Mapped[DateTime] = mapped_column(
        'Дата измерения', DateTime(timezone=True), nullable=False
    )
    date = mapped_column(
        'Дата обновления',
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    pet: Mapped['PetOrm'] = relationship('PetOrm', back_populates='lengths')


class MoltingPetOrm(Base):
    __tablename__ = 'molting_pet'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    pet_id: Mapped[int] = mapped_column(ForeignKey('pet.id'), nullable=False)
    date_measure: Mapped[DateTime] = mapped_column(
        'Дата линьки', DateTime(timezone=True), nullable=False
    )
    description: Mapped[str] = mapped_column(nullable=True)
    date = mapped_column(
        'Дата обновления',
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )
    pet: Mapped['PetOrm'] = relationship('PetOrm', back_populates='molting')

