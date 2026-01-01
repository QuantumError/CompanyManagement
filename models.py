from sqlalchemy import Column, Integer, String, ForeignKey, Date
from sqlalchemy.orm import relationship
from database import Base

#SQLAlchemy table models for the database
#Note the parent-child relations
class Employer(Base):
    __tablename__ = "employers"
    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String, index=True)
    location = Column(String)
    number_of_employees = Column(Integer)
    monthly_revenue = Column(Integer, default=0)
    industry_type = Column(String)
    founded_year = Column(Integer)
    current_date = Column(Date, nullable=True)

    yearly_revenue = Column(Integer, default=0)

    employees = relationship("Employee", back_populates="employer")

    monthly_revenue_records = relationship("MonthlyRevenueRecord", back_populates="employer")

    merge_and_acquisitions_records = relationship("MergeAndAcquisitionsRecords", back_populates="employer")

class MonthlyRevenueRecord(Base):
    __tablename__ = "monthly_revenue_records"
    id = Column(Integer, primary_key=True, index=True)
    employer_id = Column(Integer, ForeignKey('employers.id'))
    revenue = Column(Integer)
    date = Column(Date)

    employer = relationship("Employer", back_populates="monthly_revenue_records")


class MergeAndAcquisitionsRecords(Base):
    __tablename__ = "merge_and_acquisitions_records"
    id = Column(Integer, primary_key=True, index=True)
    employer_id = Column(Integer, ForeignKey('employers.id'))
    merged_company = Column(String)
    type_of = Column(String)
    price = Column(Integer, nullable=True)
    date = Column(Date)

    employer = relationship("Employer", back_populates="merge_and_acquisitions_records")

class Employee(Base):
    __tablename__ = "employees"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    age = Column(Integer)
    salary = Column(Integer)

    employer_id = Column(Integer, ForeignKey('employers.id'), nullable=True)
    
    # Reference back to employer
    employer = relationship("Employer", back_populates="employees")

