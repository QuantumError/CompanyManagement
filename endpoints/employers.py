from fastapi import APIRouter
from fastapi import Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
import models, schemas
from settings import settings
from database import get_db
import pandas as pd

#Create router
router = APIRouter(
    prefix="/employers",
    tags=["employers"],
)

# Create employer to include, field and number of employees, mothly revenue, industry type, location, and founded year.
# add employers to employee
@router.post("/employers/", response_model=schemas.Employer)
def create_employer(employer: schemas.EmployerCreate, db: Session = Depends(get_db)):
    # Create employer first
    db_employer = models.Employer(
        company_name=employer.company_name,
        location=employer.location,
        number_of_employees=employer.number_of_employees,
        industry_type=employer.industry_type,
        founded_year=employer.founded_year,
        yearly_revenue = employer.yearly_revenue,
        current_date=settings.global_date if settings.global_date else None
    )
    
    db.add(db_employer)
    
    db.commit()
    db.refresh(db_employer)

    return db_employer

@router.post("/employer-from-csv/")
def upload_employer_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="File must be a CSV")

    try:
        # Read CSV into DataFrame directly
        file.file.seek(0)
        df = pd.read_csv(file.file)

        # Check expected columns
        expected_columns = ['company_name', 'location', 'number_of_employees', 'yearly_revenue', 'industry_type', 'founded_year']
        if not all(col in df.columns for col in expected_columns):
            raise HTTPException(status_code=400, detail=f"CSV must contain columns: {expected_columns}")

        # Insert into DB
        for _, row in df.iterrows():
            existing_employer = db.query(models.Employer).filter(models.Employer.company_name == row['company_name']).first()
            if not existing_employer:
                employer = models.Employer(
                    company_name=row['company_name'],
                    location=row['location'],
                    number_of_employees=int(row['number_of_employees']),
                    yearly_revenue=float(row['yearly_revenue']),
                    industry_type=row['industry_type'],
                    founded_year=int(row['founded_year']),
                    current_date=settings.global_date if settings.global_date else None
                )       
                db.add(employer)      
                db.commit()
                db.refresh(employer)

        return {"detail": f"{file.filename} uploaded and processed."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process CSV: {e}")

@router.get("/employers/", response_model=list[schemas.Employer])
def read_employers(db: Session = Depends(get_db)):
    if db.query(models.Employer).first() is None:
        raise HTTPException(status_code=400, detail="No employers in database") 
    
    return db.query(models.Employer).all()

@router.get("/employers/{employer_id}", response_model=schemas.Employer)
def read_employer(employer_id: int, db: Session = Depends(get_db)):
    employer = db.query(models.Employer).filter(models.Employer.id == employer_id).first()
    if not employer:
        raise HTTPException(status_code=404, detail="Employer not found")
    return employer

#Edit employer
@router.put("/employers/{employer_id}", response_model=schemas.Employer)
def update_employer(employer_id: int, updated_employer: schemas.EmployerCreate, db: Session = Depends(get_db)):
    employer = db.query(models.Employer).filter(models.Employer.id == employer_id).first()

    if not employer:
        raise HTTPException(status_code=404, detail="Employer not found")
    
    employer.company_name = updated_employer.company_name
    employer.location = updated_employer.location
    employer.number_of_employees = updated_employer.number_of_employees
    employer.industry_type = updated_employer.industry_type
    employer.founded_year = updated_employer.founded_year

    db.commit()
    db.refresh(employer)
    return employer

@router.delete("/employers/{employer_id}")
def delete_employer(employer_id: int, db: Session = Depends(get_db)):   
    employer = db.query(models.Employer).filter(models.Employer.id == employer_id).first()
    employee = db.query(models.Employee).all()
    if not employer:
        raise HTTPException(status_code=404, detail="Employer not found")
    #Remove employer id from employee
    for emp in employee:
        if emp.employer_id == employer_id:
            emp.employer_id = None
    db.delete(employer)
    db.commit()   
    return {"detail": "Employer removed from database"}

#Hire an employee
@router.post("/employers/{employer_id}/employees/{employee_id}",response_model=schemas.EmployeeEmployerResponse)
def add_employee_to_employer(employer_id: int, employee_id: int, db: Session = Depends(get_db)):
    employee = db.query(models.Employee).filter(models.Employee.id == employee_id).first()
    employer = db.query(models.Employer).filter(models.Employer.id == employer_id).first()

    employers = db.query(models.Employer).all()

    if not employer:
        raise HTTPException(status_code=404, detail="Employer not found")
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    #Get employee from other company
    if employee.employer_id is not None:
        for e in employers:
            if e.id == employee.employer_id:
                e.employees.remove(employee)
                e.number_of_employees -= 1

    # assign the employee to the employer
    employee.employer_id = employer_id

    # increment employer employee count
    employer.number_of_employees += 1
    employer.employees.append(employee)

    db.commit()

    # refresh both objects
    db.refresh(employee)
    db.refresh(employer)

    return {"employee": employee, "employer": employer}

#Fire employee
@router.delete("/employers/{employer_id}/employees/{employee_id}", response_model=schemas.EmployeeEmployerResponse)
def remove_employee_from_employer(employer_id: int, employee_id: int, db: Session = Depends(get_db)):
    employee = db.query(models.Employee).filter(models.Employee.id == employee_id).first()
    employer = db.query(models.Employer).filter(models.Employer.id == employer_id).first()

    if not employer:
        raise HTTPException(status_code=404, detail="Employer not found")
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    if employee.employer_id != employer_id:
        raise HTTPException(status_code=400, detail="Employee is not assigned to this employer")

    # remove the employee from the employer
    employee.employer_id = None

    # decrement employer employee count
    employer.number_of_employees -= 1
    employer.employees.remove(employee)

    db.commit()

    # refresh both objects
    db.refresh(employee)
    db.refresh(employer)

    return {"employee": employee, "employer": employer}

# Merge two companies
@router.post("/employers/merge/", response_model=schemas.Employer)
def merge_employers(merging_company_id: int, merged_company_id: int, db: Session = Depends(get_db)):
    company1 = db.query(models.Employer).filter(models.Employer.id == merging_company_id).first()
    company2 = db.query(models.Employer).filter(models.Employer.id == merged_company_id).first()

    if not company1 or not company2:
        raise HTTPException(status_code=404, detail="One or both employers not found")
    
    if company1.id == company2.id:
        raise HTTPException(status_code=400, detail="Same ID")
    
    if settings.global_date is None:
        raise HTTPException(status_code=400, detail="No date set")

    # Merge logic
    company1.number_of_employees += company2.number_of_employees
    company1.monthly_revenue += company2.monthly_revenue
    company1.yearly_revenue += company2.yearly_revenue

    # Reassign all employees using a bulk update
    db.query(models.Employee).filter(models.Employee.employer_id == company2.id).update(
        {models.Employee.employer_id: company1.id}, synchronize_session=False
    )
    db.query(models.MonthlyRevenueRecord).filter(models.MonthlyRevenueRecord.employer_id == company2.id).update(
        {models.MonthlyRevenueRecord.employer_id: company1.id}, synchronize_session=False 
    )

    merge_record = models.MergeAndAcquisitionsRecords(employer_id = company1.id, 
                                                      merged_company = company2.company_name, 
                                                      type_of = "Merge",
                                                      date = settings.global_date)
    
    company1.merge_and_acquisitions_records.append(merge_record)
    # Delete company2
    db.delete(company2)

    # Refresh company1 to get updated employees
    db.commit()

    db.refresh(company1)

    return company1

#Acquisition by company
@router.post("/employers/acquisition/", response_model=schemas.Employer)
def acquisition(acquiring_company_id: int, bought_company_id: int, price: int, db: Session = Depends(get_db)):
    company1 = db.query(models.Employer).filter(models.Employer.id == acquiring_company_id).first()
    company2 = db.query(models.Employer).filter(models.Employer.id == bought_company_id).first()

    if not company1 or not company2:
        raise HTTPException(status_code=404, detail="One or both employers not found")
    
    if company1.id == company2.id:
        raise HTTPException(status_code=400, detail="Same ID")
    
    if settings.global_date is None:
        raise HTTPException(status_code=400, detail="No date set")

    # Merge logic
    company1.number_of_employees += company2.number_of_employees
    company1.monthly_revenue += company2.monthly_revenue
    company1.yearly_revenue += company2.yearly_revenue

    # Reassign all employees using a bulk update
    db.query(models.Employee).filter(models.Employee.employer_id == company2.id).update(
        {models.Employee.employer_id: company1.id}, synchronize_session=False
    )
    db.query(models.MonthlyRevenueRecord).filter(models.MonthlyRevenueRecord.employer_id == company2.id).update(
        {models.MonthlyRevenueRecord.employer_id: company1.id}, synchronize_session=False 
    )

    merge_record = models.MergeAndAcquisitionsRecords(employer_id = company1.id, 
                                                      merged_company = company2.company_name,
                                                      type_of = "Acquisition", 
                                                      price = price,
                                                      date = settings.global_date)
    
    company1.merge_and_acquisitions_records.append(merge_record)

    db.add(merge_record)
    # Delete company2
    db.delete(company2)

    # Refresh company1 to get updated employees
    db.commit()
    db.refresh(merge_record)
    db.refresh(company1)

    return company1