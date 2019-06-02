DROP TABLE IF EXISTS oldResultByTobanEasy;

CREATE TABLE oldResultByTobanEasy (
    raceId CHAR(14),
    toban CHAR(4),
    lane TINYINT,
    oldRank1 FLOAT(5,3), 
    oldRank2 FLOAT(5,3), 
    oldRank3 FLOAT(5,3), 
    oldRank4 FLOAT(5,3), 
    oldRank5 FLOAT(5,3), 
    oldRank6 FLOAT(5,3),
    avgStartDev FLOAT(7,5),
    avgStartTime FLOAT(7,5),
    PRIMARY KEY (raceId,toban)
);
