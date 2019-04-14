DROP TABLE IF EXISTS raceinfo;

CREATE TABLE raceinfo (
    raceId CHAR(14),
    raceDate DATE,
    raceNumber TINYINT,
    raceName VARCHAR(50),
    raceGrade VARCHAR(5),
    racePlaceId CHAR(2),
    PRIMARY KEY (raceId),
    INDEX raceinfo_date_idx (raceDate)
);
  
