-- Table: cities
CREATE TABLE cities (
                        name VARCHAR(255) PRIMARY KEY,   -- City name is now the primary key
                        latitude DECIMAL(10, 6) NOT NULL,
                        longitude DECIMAL(10, 6) NOT NULL,
                        altitude INTEGER,                -- Optional: altitude
                        timezone VARCHAR(255),
                        timezone_offset INTEGER
);

-- Table: weather_data
-- Composite primary key: one record per city per time.
CREATE TABLE weather_data (
                              city_name VARCHAR(255) NOT NULL,
                              dt TIMESTAMP WITHOUT TIME ZONE NOT NULL,  -- Date/time of the record
                              temp REAL,
                              temp_min REAL,
                              temp_max REAL,
                              feels_like REAL,
                              pressure INTEGER,
                              humidity INTEGER,
                              clouds INTEGER,                            -- Cloudiness (%)
                              wind_speed REAL,
                              wind_deg INTEGER,
                              wind_gust REAL,                            -- Optional
                              rain_volume REAL,                          -- e.g., rain in mm/h
                              --raw_json JSONB,                            -- Full JSON response for caching/audit
                              created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now(),
                              PRIMARY KEY (city_name, dt),
                              FOREIGN KEY (city_name) REFERENCES cities(name) ON DELETE CASCADE
);

-- Table: weather_conditions
-- Each record links to a specific weather_data record via city_name and dt.
CREATE TABLE weather_conditions (
                                    id SERIAL PRIMARY KEY,
                                    city_name VARCHAR(255) NOT NULL,
                                    dt TIMESTAMP WITHOUT TIME ZONE NOT NULL,
                                    condition_id INTEGER,      -- API's weather condition id (if desired)
                                    main VARCHAR(100),
                                    description VARCHAR(255),
                                    icon VARCHAR(10),
                                    FOREIGN KEY (city_name, dt) REFERENCES weather_data(city_name, dt) ON DELETE CASCADE
);

-- Table: precipitation
CREATE TABLE precipitation (
                               id SERIAL PRIMARY KEY,
                               city_name VARCHAR(255) NOT NULL,
                               dt TIMESTAMP WITHOUT TIME ZONE NOT NULL,
                               type VARCHAR(10) CHECK (type IN ('rain', 'snow')),
                               volume REAL,               -- measured in mm/h
                               FOREIGN KEY (city_name, dt) REFERENCES weather_data(city_name, dt) ON DELETE CASCADE
);

-- Recommended indexes for efficient lookups:
CREATE INDEX idx_weather_data_city_dt ON weather_data(city_name, dt);
CREATE INDEX idx_cities_lat_long ON cities(latitude, longitude);
CREATE INDEX idx_weather_conditions_data ON weather_conditions(city_name, dt);
CREATE INDEX idx_precipitation_data ON precipitation(city_name, dt);
