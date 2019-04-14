DROP TABLE IF EXISTS raceodds;

CREATE TABLE raceodds (
    raceId CHAR(14),
    oddsType VARCHAR(10),
    funaken VARCHAR(5),
    odds FLOAT(5,1),
    PRIMARY KEY (raceId,oddsType,funaken)
);
  