CREATE OR REPLACE VIEW gold.trip_analytics AS
SELECT
    f.trip_id,

   
    -- Date
   
    d.full_date,
    d.day,
    d.day_name,
    d.month,
    d.month_name,
    d.quarter,
    d.year,
    d.week_of_year,
    d.weekend_flag,

  
    -- Start Time

    st.full_time AS start_time,
    st.hour AS start_hour,
    st.minute AS start_minute,
    st.second AS start_second,
    st.time_period AS start_time_period,


    -- End Time
    
    et.full_time AS end_time,
    et.hour AS end_hour,
    et.minute AS end_minute,
    et.second AS end_second,
    et.time_period AS end_time_period,

    
    -- Start Station

    ss.station_id AS start_station_id,
    ss.station_name AS start_station_name,
    ss.latitude AS start_latitude,
    ss.longitude AS start_longitude,

    -- End Station
    
    es.station_id AS end_station_id,
    es.station_name AS end_station_name,
    es.latitude AS end_latitude,
    es.longitude AS end_longitude,

 
    -- User
 
    u.user_type,
    u.member_gender,
    u.member_birth_year,
    u.member_age,
    u.age_group,


    -- Bike

    f.bike_id,


    -- Trip Measures
 
    f.duration_sec,
    f.duration_min,


    -- Derived Analytics

    CASE
        WHEN f.start_station_key = f.end_station_key
        THEN 1
        ELSE 0
    END AS same_station_trip

FROM warehouse.fact_trip f

JOIN warehouse.dim_date d
    ON f.start_date_key = d.date_id

JOIN warehouse.dim_time st
    ON f.start_time_key = st.time_key

JOIN warehouse.dim_time et
    ON f.end_time_key = et.time_key

JOIN warehouse.dim_station ss
    ON f.start_station_key = ss.station_key

JOIN warehouse.dim_station es
    ON f.end_station_key = es.station_key

JOIN warehouse.dim_user u
    ON f.user_key = u.user_key;



