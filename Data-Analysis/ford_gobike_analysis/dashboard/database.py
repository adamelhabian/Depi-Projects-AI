import os
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)


def load_dashboard_data():
    return pd.read_sql(
        "SELECT * FROM gold.trip_analytics",
        engine
    )