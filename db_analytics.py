from fastapi import Depends
from sqlalchemy import select, func
from database import get_db
from sqlalchemy.orm import Session
from models import Employer, Employee, MonthlyRevenueRecord, MergeAndAcquisitionsRecords


#Get get the company KPIs (key performance indicators) from the database and return them.
#This is done with SQL parent-child subquery

def company_kpis(db: Session = Depends(get_db())):
    monthly_count = (
        select(
            MonthlyRevenueRecord.employer_id,
            func.count(MonthlyRevenueRecord.id).label("months_reported"),
        )
        .group_by(MonthlyRevenueRecord.employer_id)
        .subquery()
    )

    employee_count = (
            select(
                Employee.employer_id,
                func.count(Employee.id).label("employees_hired"),
            )
            .group_by(Employee.employer_id)
            .subquery()
        )

    mna_count = (
            select(
                MergeAndAcquisitionsRecords.employer_id,
                func.count(MergeAndAcquisitionsRecords.id).label("merges_and_acquisitions"),
            )
            .group_by(MergeAndAcquisitionsRecords.employer_id)
            .subquery()
        )

    stmt = (
    select(
        Employer.id,
        Employer.company_name,
        Employer.yearly_revenue,

        func.coalesce(
            monthly_count.c.months_reported, 0
        ).label("months_reported"),

        func.coalesce(
            employee_count.c.employees_hired, 0
        ).label("employees_hired"),

        func.coalesce(
            mna_count.c.merges_and_acquisitions, 0
        ).label("merges_and_acquisitions"),
    )
    .outerjoin(monthly_count, monthly_count.c.employer_id == Employer.id)
    .outerjoin(employee_count, employee_count.c.employer_id == Employer.id)
    .outerjoin(mna_count, mna_count.c.employer_id == Employer.id)
)


    result = db.execute(stmt).mappings().all()
    return result