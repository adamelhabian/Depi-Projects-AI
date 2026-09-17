-- create dim_date table
CREATE TABLE warehouse.dim_date (
    date_id INTEGER PRIMARY KEY,
    full_date DATE NOT NULL UNIQUE,

    day INTEGER NOT NULL,
    day_name VARCHAR(10) NOT NULL,

    month INTEGER NOT NULL,
    month_name VARCHAR(10) NOT NULL,

    quarter INTEGER NOT NULL,
    year INTEGER NOT NULL,

    week_of_year INTEGER NOT NULL,

    weekend_flag INTEGER NOT NULL
);


CREATE TABLE warehouse.dim_time (
    time_key SERIAL PRIMARY KEY,

    full_time TIME NOT NULL UNIQUE,

    hour INTEGER NOT NULL,
    minute INTEGER NOT NULL,
    second INTEGER NOT NULL,

    time_period VARCHAR(20) NOT NULL
);




-- create dim_station table
CREATE TABLE warehouse.dim_station (
    station_key SERIAL PRIMARY KEY,

    station_id INTEGER NOT NULL UNIQUE,
    station_name VARCHAR(255) NOT NULL,

    latitude NUMERIC(9,6) NOT NULL,
    longitude NUMERIC(9,6) NOT NULL
);



-- create dim user table 
CREATE TABLE warehouse.dim_user (
    user_key SERIAL PRIMARY KEY,

    member_birth_year INTEGER NOT NULL,
    member_age INTEGER NOT NULL,
    member_gender VARCHAR(50) NOT NULL,
    age_group VARCHAR(20) NOT NULL,
    user_type VARCHAR(50) NOT NULL,

    UNIQUE (
        member_birth_year,
        member_age,
        member_gender,
        age_group,
        user_type
    )
);





