-- RELACNI MODEL DATABAZE



-- ??????? nutno zmenit schema podle pouzityhho weather api codu
-- spanek json format je silne zpoplatneny ???????????????
-- studentska api licence


-- table weather_data
-- main table
-- weather data for 1 single day for a specific city
-- Najít místa, kde v daný den byl největší rozdíl teplot:
-- najit weather data kde temp value je nejmensi a nejvetsi, pak left join s tabulkou cities
CREATE TABLE weather_data (
                              id SERIAL PRIMARY KEY,
                              created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, -- timestamp for retention policy
                              city_id INTEGER REFERENCES cities(id),

                              -- dt: cas podle ktereho, dotazujeme open weather api a vyhledavame v db
                              dt TIMESTAMP WITHOUT TIME ZONE NOT NULL,
                              sunrise TIMESTAMP WITHOUT TIME ZONE,
                              sunset TIMESTAMP WITHOUT TIME ZONE,
                              -- timezone offset lze spocitat pres spojeni s tabulkou cities

                              -- weather data
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
                              -- raw_data JSONB     -- Optional: store the complete JSON response for further analysis
                              -- realne by pouziti jsonb formatu bylo lepsi nez pouzivat celou novou databazi...
);


-- table cities
-- nesmi se smazat v pripade smazani weather data,
-- ale pokud neexistuje zadna weather data co by ji referencovala = smazat ano
CREATE TABLE cities (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(255) NOT NULL,
                        latitude DECIMAL(8, 5) NOT NULL,
                        longitude DECIMAL(8, 5) NOT NULL,
                        timezone VARCHAR(255),
                        timezone_offset INTEGER
);


-- Create table weather_conditions
-- Najít dny v definovaném rozmezí,
-- kdy pro dané místo bylo stále stejné počasí zadané
-- jako parametr a pro tyto dny z JSON získat parametry clouds a cnt
CREATE TABLE weather_conditions (
                                    id SERIAL PRIMARY KEY,
                                    weather_data_id INTEGER REFERENCES weather_data(id),
                                    condition_id INTEGER, -- neni odkaz na tabulku, jen to je random id z jsonu
                                    main VARCHAR(100),
                                    description VARCHAR(255),
                                    icon VARCHAR(50)
);


-- table precipitation
-- Všechna místa kde v daný den nebo rozmezí dnů pršelo s danou intenzitou. ; jednoduchy pristup
-- left join na weather_data --> left join na cities
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
