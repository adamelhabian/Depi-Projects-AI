CREATE TABLE silver.trips (
    duration_sec INTEGER NOT NULL,
    duration_min NUMERIC(10,2) NOT NULL,

    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL,

    start_station_id INTEGER,
    start_station_name VARCHAR(255),
    start_station_latitude NUMERIC(9,6) NOT NULL,
    start_station_longitude NUMERIC(9,6) NOT NULL,

    end_station_id INTEGER,
    end_station_name VARCHAR(255),
    end_station_latitude NUMERIC(9,6) NOT NULL,
    end_station_longitude NUMERIC(9,6) NOT NULL,

    bike_id VARCHAR(50) NOT NULL,

    user_type VARCHAR(50) NOT NULL,
    member_birth_year INTEGER NOT NULL,
    member_age INTEGER NOT NULL,
    member_gender VARCHAR(50) NOT NULL,
    age_group VARCHAR(20) NOT NULL,

    bike_share_for_all_trip VARCHAR(10) NOT NULL
);
SELECT *
FROM silver.trips
LIMIT 5;