from decimal import Decimal

from sqlalchemy import String, ForeignKey, Text, Numeric, DateTime, Date
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from datetime import datetime, date

class Base(DeclarativeBase):
    pass

class Project(Base):
    __tablename__ = 'projects'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(150))
    start_date: Mapped[date] = mapped_column(Date, default=date.today)

    employees: Mapped[list["Employee"]] = relationship(
        "Employee",
        back_populates="projects",
        secondary="participations",)

class Employee(Base):
    __tablename__ = 'employees'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(120), unique=True)

    projects: Mapped[list["Project"]] = relationship(
        back_populates="employees",
        secondary="participations",
    )

class Participation(Base):
    __tablename__ = 'participations'

    project_id: Mapped[int] = mapped_column(ForeignKey('projects.id'), primary_key=True)
    employee_id: Mapped[int] = mapped_column(ForeignKey('employees.id'), primary_key=True)
    role: Mapped[str] = mapped_column(String(50))