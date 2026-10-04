import pandas as pd


def extract_bronze():
    return pd.read_csv(
        "data/raw/fordgobike-tripdata.csv"
    )


def extract_dates():
    return pd.read_csv(
        "data/raw/201902-fordgobike-tripdata.csv"
    )