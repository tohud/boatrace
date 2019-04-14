DROP TABLE IF EXISTS raceinfo;

CREATE TABLE raceinfo (
    raceId CHAR(14),
    raceDate DATE,
    raceNumber TINYINT,
    raceName VARCHAR(80),
    raceGrade VARCHAR(5),
    racePlaceId CHAR(2),
    raceTemperature FLOAT(3,2),
    raceWeather VARCHAR(10),
    raceWindSpeed FLOAT(3,1),
    raceSurfaceTemperature FLOAT(3,2),
    raceWaveHeight TINYINT,
    PRIMARY KEY (raceId),
    INDEX raceinfo_date_idx (raceDate)
);
  
