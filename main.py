from fastapi import FastAPI
from endpoints import employers, employees, dates, analytic_enpoint, data_visualization
from database import engine, Base

# Create tables
Base.metadata.create_all(bind=engine)

#The main API and routers
app = FastAPI(title="FastAPI SQLite CRUD Example")
       
app.include_router(employers.router)
app.include_router(employees.router)
app.include_router(dates.router)
app.include_router(analytic_enpoint.router)
app.include_router(data_visualization.router)