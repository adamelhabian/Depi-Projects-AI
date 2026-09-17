import os
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# =========================================
# Database Connection
# =========================================

def get_engine():
    return create_engine(DATABASE_URL)


# =========================================
# Bronze
# =========================================

def load_bronze(df, engine):
    """
    Load raw DataFrame into bronze.trips.

    Bronze is a raw layer, so no transformation
    is performed here.
    """

    # Clear previous Bronze snapshot
    with engine.begin() as connection:
        connection.execute(
            text("TRUNCATE TABLE bronze.trips")
        )

    # Load raw data
    df.to_sql(
        "trips",
        engine,
        schema="bronze",
        if_exists="append",
        index=False
    )

    print(
        f"Loaded {len(df)} rows into bronze.trips"
    )


# =========================================
# Silver
# =========================================

def load_to_silver(df, engine):
    """
    Load transformed DataFrame into silver.trips.
    """

    # Clear previous Silver data
    with engine.begin() as connection:
        connection.execute(
            text("TRUNCATE TABLE silver.trips")
        )

    # Load transformed data
    df.to_sql(
        "trips",
        engine,
        schema="silver",
        if_exists="append",
        index=False
    )

    print(
        f"Loaded {len(df)} rows into silver.trips"
    )


# =========================================
# Warehouse - Dimensions
# =========================================

def load_dimensions(engine):
    """
    Populate all warehouse dimension tables
    from silver.trips.
    """

    with engine.begin() as connection:

        # ---------------------------------
        # Clear existing dimensions
        # ---------------------------------

        connection.execute(
            text("TRUNCATE TABLE warehouse.fact_trip")
        )

        connection.execute(
            text("TRUNCATE TABLE warehouse.dim_date CASCADE")
        )

        connection.execute(
            text("TRUNCATE TABLE warehouse.dim_time CASCADE")
        )

        connection.execute(
            text("TRUNCATE TABLE warehouse.dim_station CASCADE")
        )

        connection.execute(
            text("TRUNCATE TABLE warehouse.dim_user CASCADE")
        )

        # ---------------------------------
        # dim_date
        # ---------------------------------

        connection.execute(
            text("""
                INSERT INTO warehouse.dim_date (
                    date_id,
                    full_date,
                    day,
                    day_name,
                    month,
                    month_name,
                    quarter,
                    year,
                    week_of_year,
                    weekend_flag
                )
                SELECT DISTINCT
                    TO_CHAR(
                        start_time::DATE,
                        'YYYYMMDD'
                    )::INTEGER AS date_id,

                    start_time::DATE AS full_date,

                    EXTRACT(
                        DAY FROM start_time
                    )::INTEGER AS day,

                    TRIM(
                        TO_CHAR(start_time, 'Day')
                    ) AS day_name,

                    EXTRACT(
                        MONTH FROM start_time
                    )::INTEGER AS month,

                    TRIM(
                        TO_CHAR(start_time, 'Month')
                    ) AS month_name,

                    EXTRACT(
                        QUARTER FROM start_time
                    )::INTEGER AS quarter,

                    EXTRACT(
                        YEAR FROM start_time
                    )::INTEGER AS year,

                    EXTRACT(
                        WEEK FROM start_time
                    )::INTEGER AS week_of_year,

                    CASE
                        WHEN EXTRACT(
                            ISODOW FROM start_time
                        ) IN (6, 7)
                        THEN 1
                        ELSE 0
                    END AS weekend_flag

                FROM silver.trips
                WHERE start_time IS NOT NULL;
            """)
        )

        # ---------------------------------
        # dim_time
        # ---------------------------------

        connection.execute(
            text("""
                INSERT INTO warehouse.dim_time (
                    full_time,
                    hour,
                    minute,
                    second,
                    time_period
                )
                SELECT DISTINCT

                    timestamp_value::TIME
                        AS full_time,

                    EXTRACT(
                        HOUR FROM timestamp_value
                    )::INTEGER AS hour,

                    EXTRACT(
                        MINUTE FROM timestamp_value
                    )::INTEGER AS minute,

                    EXTRACT(
                        SECOND FROM timestamp_value
                    )::INTEGER AS second,

                    CASE
                        WHEN EXTRACT(
                            HOUR FROM timestamp_value
                        ) BETWEEN 0 AND 5
                            THEN 'Night'

                        WHEN EXTRACT(
                            HOUR FROM timestamp_value
                        ) BETWEEN 6 AND 11
                            THEN 'Morning'

                        WHEN EXTRACT(
                            HOUR FROM timestamp_value
                        ) BETWEEN 12 AND 17
                            THEN 'Afternoon'

                        ELSE 'Evening'
                    END AS time_period

                FROM (
                    SELECT start_time AS timestamp_value
                    FROM silver.trips
                    WHERE start_time IS NOT NULL

                    UNION

                    SELECT end_time AS timestamp_value
                    FROM silver.trips
                    WHERE end_time IS NOT NULL
                ) AS timestamps;
            """)
        )

        # ---------------------------------
        # dim_station
        # ---------------------------------

        connection.execute(
            text("""
                INSERT INTO warehouse.dim_station (
                    station_id,
                    station_name,
                    latitude,
                    longitude
                )
                SELECT DISTINCT
                    station_id,
                    station_name,
                    latitude,
                    longitude

                FROM (
                    SELECT
                        start_station_id
                            AS station_id,

                        start_station_name
                            AS station_name,

                        start_station_latitude
                            AS latitude,

                        start_station_longitude
                            AS longitude

                    FROM silver.trips

                    UNION

                    SELECT
                        end_station_id
                            AS station_id,

                        end_station_name
                            AS station_name,

                        end_station_latitude
                            AS latitude,

                        end_station_longitude
                            AS longitude

                    FROM silver.trips
                ) AS stations

                WHERE station_id IS NOT NULL;
            """)
        )

        # ---------------------------------
        # dim_user
        # ---------------------------------

        connection.execute(
            text("""
                INSERT INTO warehouse.dim_user (
                    member_birth_year,
                    member_age,
                    member_gender,
                    age_group,
                    user_type
                )
                SELECT DISTINCT
                    member_birth_year,
                    member_age,
                    member_gender,
                    age_group,
                    user_type

                FROM silver.trips;
            """)
        )

    print("Warehouse dimensions loaded successfully.")


# =========================================
# Warehouse - Fact
# =========================================

def load_fact(engine):
    """
    Populate warehouse.fact_trip from silver.trips
    using the warehouse dimensions.
    """

    with engine.begin() as connection:

        # Clear existing fact data
        connection.execute(
            text("TRUNCATE TABLE warehouse.fact_trip")
        )

        # Load fact table
        connection.execute(
            text("""
                INSERT INTO warehouse.fact_trip (
                    start_date_key,
                    end_date_key,

                    start_time_key,
                    end_time_key,

                    start_station_key,
                    end_station_key,

                    user_key,

                    bike_id,

                    duration_sec,
                    duration_min,

                    start_time,
                    end_time
                )

                SELECT

                    start_date.date_id
                        AS start_date_key,

                    end_date.date_id
                        AS end_date_key,

                    start_time.time_key
                        AS start_time_key,

                    end_time.time_key
                        AS end_time_key,

                    start_station.station_key
                        AS start_station_key,

                    end_station.station_key
                        AS end_station_key,

                    u.user_key,

                    s.bike_id,

                    s.duration_sec,
                    s.duration_min,

                    s.start_time,
                    s.end_time

                FROM silver.trips s

                JOIN warehouse.dim_date start_date
                    ON start_date.full_date =
                       s.start_time::DATE

                JOIN warehouse.dim_date end_date
                    ON end_date.full_date =
                       s.end_time::DATE

                JOIN warehouse.dim_time start_time
                    ON start_time.full_time =
                       s.start_time::TIME

                JOIN warehouse.dim_time end_time
                    ON end_time.full_time =
                       s.end_time::TIME

                JOIN warehouse.dim_station start_station
                    ON start_station.station_id =
                       s.start_station_id

                JOIN warehouse.dim_station end_station
                    ON end_station.station_id =
                       s.end_station_id

                JOIN warehouse.dim_user u
                    ON u.member_birth_year =
                       s.member_birth_year

                    AND u.member_age =
                        s.member_age

                    AND u.member_gender =
                        s.member_gender

                    AND u.age_group =
                        s.age_group

                    AND u.user_type =
                        s.user_type;
            """)
        )

    print("Warehouse fact table loaded successfully.")


# =========================================
# Validation
# =========================================

def validate_load(engine):
    """
    Check row counts across pipeline layers.
    """

    with engine.connect() as connection:

        bronze_count = connection.execute(
            text("""
                SELECT COUNT(*)
                FROM bronze.trips
            """)
        ).scalar()

        silver_count = connection.execute(
            text("""
                SELECT COUNT(*)
                FROM silver.trips
            """)
        ).scalar()

        fact_count = connection.execute(
            text("""
                SELECT COUNT(*)
                FROM warehouse.fact_trip
            """)
        ).scalar()

        date_count = connection.execute(
            text("""
                SELECT COUNT(*)
                FROM warehouse.dim_date
            """)
        ).scalar()

        time_count = connection.execute(
            text("""
                SELECT COUNT(*)
                FROM warehouse.dim_time
            """)
        ).scalar()

        station_count = connection.execute(
            text("""
                SELECT COUNT(*)
                FROM warehouse.dim_station
            """)
        ).scalar()

        user_count = connection.execute(
            text("""
                SELECT COUNT(*)
                FROM warehouse.dim_user
            """)
        ).scalar()

    print("\n========== PIPELINE VALIDATION ==========")

    print(f"Bronze rows : {bronze_count}")
    print(f"Silver rows : {silver_count}")
    print(f"Fact rows   : {fact_count}")

    print(f"\nDate dimension    : {date_count}")
    print(f"Time dimension    : {time_count}")
    print(f"Station dimension : {station_count}")
    print(f"User dimension    : {user_count}")

    print("=========================================\n")


# =========================================
# Standalone Test
# =========================================

if __name__ == "__main__":

    engine = get_engine()

    print("Testing load.py...")

    # Read existing Bronze
    df = pd.read_sql(
        "SELECT * FROM bronze.trips",
        engine
    )

    # Read timestamp source
    df_dates = pd.read_csv(
        "data/raw/201902-fordgobike-tripdata.csv"
    )

    # Transform Bronze -> Silver
    from transform import transform_to_silver

    silver_df = transform_to_silver(
        df,
        df_dates
    )

    # Load Silver
    load_to_silver(
        silver_df,
        engine
    )

    # Load dimensions
    load_dimensions(
        engine
    )

    # Load fact
    load_fact(
        engine
    )

    # Validate
    validate_load(
        engine
    )
