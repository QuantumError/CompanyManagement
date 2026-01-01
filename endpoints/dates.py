from fastapi import APIRouter
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
import models, schemas
from settings import settings
from database import get_db

from dateutil.relativedelta import relativedelta
import datetime

router = APIRouter(
    prefix="/dates",
    tags=["dates"],
)

@router.post("/set-date/", response_model=schemas.DateSet)
def set_date(date: str, db: Session = Depends(get_db)):   
    try:
        date_obj = datetime.datetime.strptime(date, '%Y-%m-%d')
        settings.global_date = date_obj 

        employers = db.query(models.Employer).all()

        if employers:
            for employer in employers:
                if employer.current_date is None:
                    employer.current_date = date_obj
                    db.add(employer)      
                    db.commit()
                    db.refresh(employer)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Not correct date: {e}")

    return {"my_date": date_obj.strftime('%Y-%m-%d')}

#Update the date
@router.put("/update-date/")
async def update_date():
    if settings.global_date is None:
        raise HTTPException(status_code=400, detail="Date not set")
    settings.global_date += relativedelta(months=1)

    return {"detail": f"Date updated to {settings.global_date.strftime('%Y-%m-%d')}"}

#Update monthly revenues
@router.put("/update-company-revenues/")
async def update_company_revenues(id: int, add_to_revenue: int, db: Session = Depends(get_db)):
    if settings.global_date is None:
        raise HTTPException(status_code=400, detail="Date not set")

    date_set = settings.global_date

    employer = db.query(models.Employer).filter(models.Employer.id == id).first()
    if not employer:
        raise HTTPException(status_code=404, detail="Employer not found")

    # First-of-year reset logic
    is_new_year = (date_set.month == 1 and employer.current_date is not None and employer.current_date.year != date_set.year)

    # Case 1: New year → reset yearly revenue
    if is_new_year:
        employer.yearly_revenue = 0

    # Monthly update logic
    employer.current_date = date_set
    employer.monthly_revenue = add_to_revenue
    employer.yearly_revenue += add_to_revenue

    # Create monthly revenue record
    monthly_record = models.MonthlyRevenueRecord(
        employer_id=employer.id,
        revenue=add_to_revenue,
        date=date_set
    )

    employer.monthly_revenue_records.append(monthly_record)
    #db.add(monthly_record)
    db.commit()

    db.refresh(monthly_record)
    db.refresh(employer)

    return {
        "detail": f"Monthly revenue updated for employer ID {id}",
        "month": date_set.month,
        "year": date_set.year,
        "monthly_revenue": add_to_revenue,
        "yearly_revenue": employer.yearly_revenue,
    }


@router.get("/get-date/", response_model=schemas.DateSet)
def get_date():
    if settings.global_date is None:
        raise HTTPException(status_code=400, detail="Date not set")
    return {"my_date": settings.global_date.strftime('%Y-%m-%d')}
