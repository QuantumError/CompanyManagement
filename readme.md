# Introduction

This is a small FastAPI backend with SQLAlchemy and SQLite database. It features and ETL pipeline that can read .csv files into the database.

# How to use

This project uses FastAPI with SQLite and SQLAlchemy, with a CRUD architecture and ETL pipelines.
The project is only a backend, without clear visuals, but you can try it out with
'python -m fastapi dev main.py' and select the /docs, which shows the Swagger UI navigation.

The project is structured as a relational database that works within the API.

Recommended endpoint use order is: set-date -> read employer csv and read employee csv -> add employee to employer -> monthly revenue update -> merge etc. -> update date -> update monthly revenue -> .. -> visualize monthly revenue -> .. -> last get company KPIs
