DROP TABLE IF EXISTS racebeforeinfo;

CREATE TABLE racebeforeinfo (
    raceId CHAR(14),
    raceTemperature FLOAT(4,1),
    raceWeather VARCHAR(10),
    raceWindSpeed FLOAT(3,1),
    raceSurfaceTemperature FLOAT(4,1),
    raceWaveHeight TINYINT,
    PRIMARY KEY (raceId)
);
  
