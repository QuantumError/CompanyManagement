from pydantic_settings import BaseSettings   
from typing import Optional
from datetime import date

#Global variables used in the API, used to store per-session
class Settings(BaseSettings):
    global_date: Optional[date] = None
    check_endpoint: bool = False

settings = Settings()