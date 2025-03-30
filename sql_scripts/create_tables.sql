-- Create table cities -- nesmi se smazat v pripade smazani weather data,
-- ale pokud neexistuje zadna weather data co by ji referencovala = smazat ano
CREATE TABLE cities (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(255) NOT NULL,
                        latitude DECIMAL(8, 5) NOT NULL,
                        longitude DECIMAL(8, 5) NOT NULL,
                        timezone VARCHAR(255),
                        timezone_offset INTEGER
);

-- Create table weather_data
CREATE TABLE weather_data (
                              id SERIAL PRIMARY KEY,
                              city_id INTEGER REFERENCES cities(id),
                              dt TIMESTAMP WITHOUT TIME ZONE NOT NULL,
                              sunrise TIMESTAMP WITHOUT TIME ZONE,
                              sunset TIMESTAMP WITHOUT TIME ZONE,
                              temp REAL,
                              feels_like REAL,
                              pressure INTEGER,
                              humidity INTEGER,
                              dew_point REAL,
                              clouds INTEGER,
                              uvi REAL,
                              visibility INTEGER,
                              wind_speed REAL,
                              wind_gust REAL,
                              wind_deg INTEGER,
                              cnt INTEGER           -- , Extra field for the count parameter from JSON (if available)
                              -- raw_data JSONB         -- Optional: store the complete JSON response for further analysis
);

-- Create table weather_conditions -- main table -- referencuje data a conditions
CREATE TABLE weather_conditions (
                                    id SERIAL PRIMARY KEY,
                                    record_inserted_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, -- required for data retention
                                    weather_data_id INTEGER REFERENCES weather_data(id),
                                    condition_id INTEGER,
                                    main VARCHAR(100),
                                    description VARCHAR(255),
                                    icon VARCHAR(50)
);

-- Create table precipitation -- nutno predelat
CREATE TABLE precipitation (
                               id SERIAL PRIMARY KEY,
                               weather_data_id INTEGER REFERENCES weather_data(id),
                               type VARCHAR(10) CHECK (type IN ('rain', 'snow')),
                               volume REAL  -- measured in mm/h
);

-- Recommended indexes for fast lookups:
CREATE INDEX idx_weather_data_city_dt ON weather_data(city_id, dt);
CREATE INDEX idx_cities_lat_long ON cities(latitude, longitude);
CREATE INDEX idx_weather_conditions_data ON weather_conditions(weather_data_id);
CREATE INDEX idx_precipitation_data ON precipitation(weather_data_id);
