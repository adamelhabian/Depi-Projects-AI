from extract import extract_bronze, extract_dates
from transform import transform_to_silver
from load import (
    get_engine,
    initialize_database,
    load_bronze,
    load_to_silver,
    load_dimensions,
    load_fact,
    validate_load
)


def run_pipeline():

    print("\n========== PIPELINE START ==========\n")

    # =========================================
    # 1. Extract
    # =========================================

    print("1. Extracting raw data...")

    bronze_df = extract_bronze()
    dates_df = extract_dates()

    print(f"Bronze source rows: {len(bronze_df)}")
    print(f"Dates source rows: {len(dates_df)}")

    # =========================================
    # 2. Database Connection
    # =========================================

    engine = get_engine()
    # =========================================
    # 3. Initialize Database
    # =========================================

    print("\n2. Initializing database structure...")

    initialize_database(
        engine
    )

    # =========================================
    # 4. Load Bronze
    # =========================================

    print("\n2. Loading Bronze...")

    load_bronze(
        bronze_df,
        engine
    )

    # =========================================
    # 4. Transform Bronze → Silver
    # =========================================

    print("\n3. Transforming Bronze → Silver...")

    silver_df = transform_to_silver(
        bronze_df,
        dates_df
    )

    print(
        f"Silver rows after transformation: "
        f"{len(silver_df)}"
    )

    # =========================================
    # 5. Load Silver
    # =========================================

    print("\n4. Loading Silver...")

    load_to_silver(
        silver_df,
        engine
    )

    # =========================================
    # 6. Load Warehouse Dimensions
    # =========================================

    print("\n5. Loading warehouse dimensions...")

    load_dimensions(
        engine
    )

    # =========================================
    # 7. Load Fact
    # =========================================

    print("\n6. Loading fact table...")

    load_fact(
        engine
    )

    # =========================================
    # 8. Validation
    # =========================================

    print("\n7. Validating pipeline...")

    validate_load(
        engine
    )

    print("========== PIPELINE COMPLETE ==========\n")


if __name__ == "__main__":
    run_pipeline()