from typing import List, Optional
from pydantic import BaseModel
from datetime import date

#Pydantic Schemas for FastAPI

# Employee items
class EmployeeBase(BaseModel):
    name: str
    age: int
    salary: int

class EmployeeCreate(EmployeeBase):
    pass

class Employee(EmployeeBase):
    id: int
    employer_id: int | None = None

    class Config:
        orm_mode = True

# Employer items
class EmployerBase(BaseModel):
    company_name: str
    location: str   
    number_of_employees: int
    industry_type: str
    founded_year: int
    yearly_revenue: int


class EmployerCreate(EmployerBase):
    pass

class DateSet(BaseModel):
    my_date: str

class MonthRevenueBase(BaseModel):
    revenue: float

class MonthlyRevenue(MonthRevenueBase):
    id: int
    employer_id: int
    date: date

    class Config:
        orm_mode = True

class MergeRecords(BaseModel):
    id: int
    employer_id: int
    merged_company: str
    type_of: str
    price: Optional[int]
    date: date

    class Config:
        orm_mode = True

class Employer(EmployerBase):
    id: int
    current_date: Optional[date] = None
    monthly_revenue: float = 0

    employees: List[Employee] = []

    monthly_revenue_records: List[MonthlyRevenue] = []

    merge_and_acquisitions_records: List[MergeRecords] = []

    class Config:
        orm_mode = True

class EmployeeEmployerResponse(BaseModel):
    employee: Employee
    employer: Employer    



    