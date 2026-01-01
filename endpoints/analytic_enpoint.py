from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db_analytics import company_kpis
from fastapi.responses import StreamingResponse
from database import get_db
import pandas as pd
from models import Employer
from settings import settings
import io

router = APIRouter(prefix="/analytics", tags=["analytics"])

#Print all the KPIs
@router.get("/companies")
def get_company_kpis(db: Session = Depends(get_db)):
    
    if db.query(Employer).first() is None:
        raise HTTPException(status_code=400, detail="Empty database") 

    return company_kpis(db)

#Get yearly report to csv
@router.put("/companies")
def yearly_report_to_csv(db: Session = Depends(get_db)):
    if db.query(Employer).first() is None:
        raise HTTPException(status_code=400, detail="Empty database") 

    if settings.global_date is not None:
        kpis = company_kpis(db)

        # Convert to DataFrame
        df = pd.DataFrame(kpis)

        # Create CSV in memory
        buffer = io.StringIO()
        df.to_csv(buffer, index=False)
        buffer.seek(0)

        return StreamingResponse(
            buffer,
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename={settings.global_date.strftime('%Y-%m-%d')}_yearly_report.csv"
            },
        )
    else:
        return {"Date not set"}