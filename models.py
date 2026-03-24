from sqlalchemy import (
    Column, Integer, String, Float, DateTime, ForeignKey, func,
    UniqueConstraint, Index
)
from sqlalchemy.orm import relationship
from db import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String(120), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    calculations = relationship(
        "Calculation",
        back_populates="user",
        cascade="all,delete",
        passive_deletes=True,
    )
    sessions = relationship(
        "UserSession",
        back_populates="user",
        cascade="all,delete",
        passive_deletes=True,
    )

class RiskLevel(Base):
    __tablename__ = "risk_levels"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False, unique=True)
    expected_return = Column(Float, nullable=True)
    description = Column(String(255), nullable=True)

    calculations = relationship(
        "Calculation",
        back_populates="risk_level"
    )

class Calculation(Base):
    __tablename__ = "calculations"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    title = Column(String(255), nullable=False)
    initial_amount = Column(Float, nullable=False)
    monthly_contribution = Column(Float, nullable=False)
    annual_rate = Column(Float, nullable=False)
    years = Column(Integer, nullable=False)

    final_amount = Column(Float, nullable=False)
    total_contributions = Column(Float, nullable=False)
    profit = Column(Float, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="calculations")

    risk_level_id = Column(Integer, ForeignKey("risk_levels.id"), nullable=True)
    risk_level = relationship("RiskLevel", back_populates="calculations")

    years_rows = relationship(
        "CalculationYear",
        back_populates="calculation",
        cascade="all,delete-orphan",
        passive_deletes=True,
        order_by="CalculationYear.year",
    )

class CalculationYear(Base):
    __tablename__ = "calculation_years"
    id = Column(Integer, primary_key=True)
    calculation_id = Column(Integer, ForeignKey("calculations.id", ondelete="CASCADE"), nullable=False)

    year = Column(Integer, nullable=False)           # 1..N
    total = Column(Float, nullable=False)
    contributions = Column(Float, nullable=False)
    profit = Column(Float, nullable=False)

    calculation = relationship("Calculation", back_populates="years_rows")

    __table_args__ = (
        UniqueConstraint("calculation_id", "year", name="uq_calc_year"),
        Index("ix_calc_year_calcid_year", "calculation_id", "year"),
    )


class UserSession(Base):
    __tablename__ = "user_sessions"

    id = Column(Integer, primary_key=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    token = Column(String(512), nullable=False, unique=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)

    user = relationship(
        "User",
        back_populates="sessions"
    )