
--- CREATE FACT_TRIP
CREATE TABLE warehouse.fact_trip (
    trip_id BIGSERIAL PRIMARY KEY,

    -- Date dimensions
    start_date_key INTEGER NOT NULL,
    end_date_key INTEGER NOT NULL,

    -- Time dimensions
    start_time_key INTEGER NOT NULL,
    end_time_key INTEGER NOT NULL,

    -- Station dimensions
    start_station_key INTEGER,
    end_station_key INTEGER,

    -- User dimension
    user_key INTEGER NOT NULL,

    -- Degenerate dimension
    bike_id VARCHAR(50) NOT NULL,

    -- Measures
    duration_sec INTEGER NOT NULL,
    duration_min NUMERIC(10,2) NOT NULL,

    -- Exact timestamps
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL,

    -- Foreign keys
    CONSTRAINT fk_start_date
        FOREIGN KEY (start_date_key)
        REFERENCES warehouse.dim_date(date_id),

    CONSTRAINT fk_end_date
        FOREIGN KEY (end_date_key)
        REFERENCES warehouse.dim_date(date_id),

    CONSTRAINT fk_start_time
        FOREIGN KEY (start_time_key)
        REFERENCES warehouse.dim_time(time_key),

    CONSTRAINT fk_end_time
        FOREIGN KEY (end_time_key)
        REFERENCES warehouse.dim_time(time_key),

    CONSTRAINT fk_start_station
        FOREIGN KEY (start_station_key)
        REFERENCES warehouse.dim_station(station_key),

    CONSTRAINT fk_end_station
        FOREIGN KEY (end_station_key)
        REFERENCES warehouse.dim_station(station_key),

    CONSTRAINT fk_user
        FOREIGN KEY (user_key)
        REFERENCES warehouse.dim_user(user_key)
);




