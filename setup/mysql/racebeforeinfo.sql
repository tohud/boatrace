DROP TABLE IF EXISTS racebeforeinfo;

CREATE TABLE racebeforeinfo (
    raceId CHAR(14),
    raceTemperature FLOAT(3,2),
    raceWeather VARCHAR(10),
    raceWindSpeed FLOAT(3,1),
    raceSurfaceTemperature FLOAT(3,2),
    raceWaveHeight TINYINT,
    PRIMARY KEY (raceId)
);
  
