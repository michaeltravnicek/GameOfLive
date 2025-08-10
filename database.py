
from __future__ import annotations
from typing import List
from sqlalchemy import create_engine

from sqlalchemy.orm import sessionmaker
import sqlalchemy as sa
from sqlalchemy.orm import DeclarativeBase


engine = create_engine("postgresql+psycopg2://citizix_user:S3cret@localhost:5432/citizix_db")


class Base(DeclarativeBase):
    pass


class Event(Base):
    __tablename__ = "event"

    id = sa.Column(sa.Integer(), autoincrement=True, primary_key=True)
    place = sa.Column(sa.String())
    date = sa.Column(sa.DateTime())


class User(Base):
    __tablename__ = "user"

    id = sa.Column(sa.Integer(), autoincrement=True, primary_key=True)
    name = sa.Column(sa.String())
    number = sa.Column(sa.Integer(), unique=True)


class UserToEvent(Base):
    __tablename__ = "user_to_event"
    
    user_id = sa.Column(sa.Integer(), sa.ForeignKey("user.id", ondelete="CASCADE"), primary_key=True)
    event_id = sa.Column(sa.Integer(), sa.ForeignKey("event.id", ondelete="CASCADE"), primary_key=True)



Base.metadata.create_all(engine)
SessionLocal = sessionmaker(bind=engine)