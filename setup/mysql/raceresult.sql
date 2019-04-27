DROP TABLE IF EXISTS raceresult;

CREATE TABLE raceresult (
    raceId CHAR(14),
    goalRank TINYINT,
    lane TINYINT,
    toban CHAR(4),
    startTime FLOAT(4,2),
    goalTime FLOAT(5,2),
    PRIMARY KEY (raceId,goalRank)
);
  
