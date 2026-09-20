import pandas as pd


def transform_to_silver(df, df_dates):

   
    # 1. Reconstruct Full Timestamps


    safe_join_cols = [
        'duration_sec',
        'start_station_id',
        'end_station_id',
        'bike_id',
        'user_type',
        'bike_share_for_all_trip'
    ]

    # Remove duplicated join keys from both datasets
    df_bronze_unique = df[
        ~df.duplicated(
            subset=safe_join_cols,
            keep=False
        )
    ]

    df_dates_unique = df_dates[
        ~df_dates.duplicated(
            subset=safe_join_cols,
            keep=False
        )
    ]

    # Merge the full timestamps into Bronze data
    df = pd.merge(
        df_bronze_unique.drop(
            columns=['start_time', 'end_time'],
            errors='ignore'
        ),
        df_dates_unique[
            safe_join_cols + ['start_time', 'end_time']
        ],
        on=safe_join_cols,
        how='inner'
    )

    # Convert timestamps
    df['start_time'] = pd.to_datetime(
        df['start_time'],
        errors='coerce'
    )

    df['end_time'] = pd.to_datetime(
        df['end_time'],
        errors='coerce'
    )

    # Remove rows with invalid timestamps
    df = df.dropna(
        subset=['start_time', 'end_time']
    )

    # Remove exact duplicate rows
    df = df.drop_duplicates()


    # 2. Data Cleaning


    # Remove missing demographic information
    df = df.dropna(
        subset=[
            'member_birth_year',
            'member_gender'
        ]
    )

    # Remove unrealistic birth years
    df = df[
        (df['member_birth_year'] >= 1939) &
        (df['member_birth_year'] <= 2001)
    ]

    # Remove unrealistic trip durations
    df = df[
        df['duration_sec'] <= 86400
    ]

   
    # 3. Data Type Standardization


    df['member_birth_year'] = (
        df['member_birth_year'].astype(int)
    )

    df['start_station_id'] = (
        df['start_station_id'].astype('Int64')
    )

    df['end_station_id'] = (
        df['end_station_id'].astype('Int64')
    )

    df['bike_id'] = (
        df['bike_id'].astype(str)
    )

    df['user_type'] = (
        df['user_type'].astype('category')
    )

    df['member_gender'] = (
        df['member_gender'].astype('category')
    )

   
    # 4. Feature Engineering
    

    # Duration in minutes
    df['duration_min'] = (
        df['duration_sec'] / 60
    ).round(2)

    # Age at the time of the dataset
    df['member_age'] = (
        2019 - df['member_birth_year']
    )

    # Age groups
    age_bins = [
        17,
        25,
        35,
        50,
        65,
        80
    ]

    age_labels = [
        '18-25',
        '26-35',
        '36-50',
        '51-65',
        '66-80'
    ]

    df['age_group'] = pd.cut(
        df['member_age'],
        bins=age_bins,
        labels=age_labels
    )

    return df



# Standalone Test


if __name__ == "__main__":
    import os
    from sqlalchemy import create_engine
    from dotenv import load_dotenv

    load_dotenv()

    DATABASE_URL = os.getenv("DATABASE_URL")

    engine = create_engine(
        DATABASE_URL
    )

    # Read Bronze
    df = pd.read_sql(
        "SELECT * FROM bronze.trips",
        engine
    )

    # Read timestamp source
    df_dates = pd.read_csv(
        "data/raw/201902-fordgobike-tripdata.csv"
    )

    # Transform
    silver_df = transform_to_silver(
        df,
        df_dates
    )

    # Validation
    print("Bronze rows:", len(df))
    print("Dates rows:", len(df_dates))
    print("Silver rows:", len(silver_df))

    print("\nColumns:")
    print(silver_df.columns.tolist())

    print(
        "\nNumber of columns:",
        len(silver_df.columns)
    )

    print("\nData types:")
    print(silver_df.dtypes)

    print("\nFirst 5 timestamps:")
    print(
        silver_df[
            ['start_time', 'end_time']
        ].head()
    )