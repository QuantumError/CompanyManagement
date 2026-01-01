from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.responses import StreamingResponse
from database import get_db
import pandas as pd
import models
import io
from plotnine import *

router = APIRouter(prefix="/visualization", tags=["visualization"])

#Visualize monthly revenues
@router.get("/monthly-revenue")
def monthly_revenue_plot(employer_id: int | None = None, db: Session = Depends(get_db)):
    query = db.query(models.MonthlyRevenueRecord)

    if employer_id:
        query = query.filter(
            models.MonthlyRevenueRecord.employer_id == employer_id
        )

    records = query.all()

    if not records:
        raise HTTPException(status_code=404, detail="No revenue data found")

    # Convert to DataFrame
    df = pd.DataFrame(
        [{
            "date": r.date,
            "revenue": r.revenue,
            "employer_id": r.employer_id
        } for r in records]
    )

    # Ensure datetime
    df["date"] = pd.to_datetime(df["date"])

    # Plot
    plot = (
        ggplot(df, aes(x="date", y="revenue", group="employer_id"))
        + geom_line()
        + geom_point()
        + labs(
            title="Monthly Revenue Over Time",
            x="Month",
            y="Revenue"
        )
        + theme_minimal()
    )

    # Render to PNG
    img = io.BytesIO()
    plot.save(img, format="png", dpi=120)
    img.seek(0)

    return StreamingResponse(img, media_type="image/png")
