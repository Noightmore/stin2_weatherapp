-- Zadani:
-- Umět získat počasí i historicky pro dané místo určené buď pomocí souřadnic, nebo názvu místa.
-- Místo, souřadnice, teploty (min,max), vlhkost, tlak, nadmořskou výšku, počasí (ikona, popis, název, kód), vítr (rychlost a směr),  déšť.
-- JSON do nosql db.
-- Stáhnout data n dní do minulosti pro dané místo.
--
-- Následně napsat aplikaci, která bude umět:
-- 1.       Dle zadání uživatele stahovat data o aktuálním počasí, n dní do minulosti pro dané místo
-- 2.       Používat relační db jako cache, tz. Pokud už daná data budu mít v db pak se  již nebudu ptát API (umět jak dle místa tak i souřadnic)
-- 3.       Nad strukturovanými daty pak umět hledat:
--      a.       Všechna místa kde v daný den nebo rozmezí dnů pršelo s danou intenzitou.
--      b.       Najít dny v definovaném rozmezí, kdy pro dané místo bylo stále stejné počasí zadané jako parametr a pro tyto dny z JSON získat parametry clouds a cnt
--      c.       Najít místa, kde v daný den byl největší rozdíl teplot
-- 4.       Navrhnou systém pro mazání záznamů z DBs dle retention period
            -- u mongo je system udelan nastavenim tvrdeho limitu dokumentu
-- 5.       Umět pro testovací účely vygenerovat n záznamů (pro ověření rychlosti mazání a vyhledávání)
            -- neni potreba a nebudu to delat
-- 6.       Navrhnout odpovídající indexy
            -- asi hotovo?
-- 7.       Používat systém pro verzování schématu relační DB (liquibase, flyway)
-- 8.       Libovolný jazyk a DB
            -- Python, PostgreSQL, MongoDB


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
                              city_name VARCHAR(255) NOT NULL, -- primarni slozeny klic
                              dt TIMESTAMP WITHOUT TIME ZONE NOT NULL, -- primarni slozeny klic; -- Date/time of the record
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
                              created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now(),
                              PRIMARY KEY (city_name, dt),
                              FOREIGN KEY (city_name) REFERENCES cities(name) ON DELETE CASCADE
);

-- Table: weather_conditions
-- Composite primary key: one record per city per time per condition.
CREATE TABLE weather_conditions (
                                    city_name VARCHAR(255) NOT NULL,
                                    dt TIMESTAMP WITHOUT TIME ZONE NOT NULL,
                                    description VARCHAR(255),
                                    icon VARCHAR(10),
                                    PRIMARY KEY (city_name, dt),
                                    FOREIGN KEY (city_name, dt) REFERENCES weather_data(city_name, dt) ON DELETE CASCADE
);

-- Table: precipitation
-- NUTNO ZJISTIT, ZDA EXISTUJE MOZNOST, ZE PRO JEDEN DEN MUZE BYT VICE ZAZNAMU SRAZEK, asi se zeptat spanka?
CREATE TABLE precipitation (
                               city_name VARCHAR(255) NOT NULL, -- primarni slozeny klic
                               dt TIMESTAMP WITHOUT TIME ZONE NOT NULL, -- primarni slozeny klic
                               type VARCHAR(10) CHECK (type IN ('rain', 'snow')),
                               volume REAL,               -- measured in mm/h
                               PRIMARY KEY (city_name, dt, type), -- lze udelat, pokud se jedna o celkovy zaznam srazek za cely den
                               FOREIGN KEY (city_name, dt) REFERENCES weather_data(city_name, dt) ON DELETE CASCADE
);

-- Recommended indexes for efficient lookups:
CREATE INDEX idx_weather_data_city_dt ON weather_data(city_name, dt);
CREATE INDEX idx_cities_lat_long ON cities(latitude, longitude);

-- kvuli bodu b)
CREATE INDEX idx_weather_conditions_data ON weather_conditions(city_name, dt);

-- kvuli bodu a)
CREATE INDEX idx_precipitation_data ON precipitation(city_name, dt);

-- kvuli bodu a) a b) a podmince umet se dotazovat dle souradnic na bod a)
CREATE INDEX idx_cities_lat_long ON cities(latitude, longitude);