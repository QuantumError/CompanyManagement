from fastapi import APIRouter
from fastapi import Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
import models, schemas
from database import get_db
import pandas as pd

router = APIRouter(
    prefix="/employees",
    tags=["employees"],
)

# Create employee
@router.post("/employees/", response_model=schemas.Employee)
def create_Employee(Employee: schemas.EmployeeCreate, db: Session = Depends(get_db)):
    db_Employee = models.Employee(
        name=Employee.name,
        age=Employee.age,
        salary=Employee.salary,
        employer_id=None 
    )
    

    db.add(db_Employee)
    db.commit()
    db.refresh(db_Employee)
    return db_Employee


@router.post("/employee-from-csv/")
def upload_employee_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="File must be a CSV")

    try:
        # Read CSV into DataFrame directly
        file.file.seek(0)
        df = pd.read_csv(file.file)

        # Check expected columns
        expected_columns = ['name', 'age', 'salary']
        if not all(col in df.columns for col in expected_columns):
            raise HTTPException(status_code=400, detail=f"CSV must contain columns: {expected_columns}")

        # Insert into DB
        for _, row in df.iterrows():
            existing_Employee = db.query(models.Employee).filter(models.Employee.name == row['name']).first()
                
            if not existing_Employee:
                Employee = models.Employee(
                    name=row['name'],
                    age=int(row['age']),
                    salary=int(row['salary']),  # make sure model uses Integer
                )
                db.add(Employee)
                db.commit()
                db.refresh(Employee)
        return {"detail": f"{file.filename} uploaded and processed."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process CSV: {e}")


# Read all
@router.get("/employee/", response_model=list[schemas.Employee])
def read_people(db: Session = Depends(get_db)):
    Employee = db.query(models.Employee).all()
    return Employee

# Read by ID
@router.get("/employees/{Employee_id}", response_model=schemas.Employee)
def read_Employee(Employee_id: int, db: Session = Depends(get_db)):
    Employee = db.query(models.Employee).filter(models.Employee.id == Employee_id).first()
    if not Employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return Employee

# Update
@router.put("/employees/{Employee_id}", response_model=schemas.Employee)
def update_Employee(Employee_id: int, updated_Employee: schemas.EmployeeCreate, db: Session = Depends(get_db)):
    Employee = db.query(models.Employee).filter(models.Employee.id == Employee_id).first()
    if not Employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    Employee.name = updated_Employee.name
    Employee.age = updated_Employee.age
    Employee.salary = updated_Employee.salary
    db.commit()
    db.refresh(Employee)
    return Employee

# Delete
@router.delete("/employees/{Employee_id}")
def delete_Employee(Employee_id: int, db: Session = Depends(get_db)):
    Employee = db.query(models.Employee).filter(models.Employee.id == Employee_id).first()
    if not Employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    db.delete(Employee)
    db.commit()
    return {"detail": "Employee removed from database"}