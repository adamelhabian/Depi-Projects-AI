CREATE TABLE bronze.trips(
   duration_sec INTEGER,
    start_time TEXT,
    end_time TEXT,

    start_station_id DOUBLE PRECISION,
    start_station_name TEXT,
    start_station_latitude DOUBLE PRECISION,
    start_station_longitude DOUBLE PRECISION,

    end_station_id DOUBLE PRECISION,
    end_station_name TEXT,
    end_station_latitude DOUBLE PRECISION,
    end_station_longitude DOUBLE PRECISION,

    bike_id INTEGER,
    user_type TEXT,

    member_birth_year DOUBLE PRECISION,
    member_gender TEXT,

    bike_share_for_all_trip TEXT

)

