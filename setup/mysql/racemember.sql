DROP TABLE IF EXISTS racemember;

CREATE TABLE racemember (
    raceId CHAR(14),
    rmLane TINYINT,
    rmToban CHAR(4),
    rmRank CHAR(2),
    rmWeight FLOAT(4,1),
    rmChoseiWeight FLOAT(4,1),
    rmTenjiTime FLOAT(3,2),
    rmStartTenjiTime FLOAT(3,2),
    PRIMARY KEY (raceId,rmLane)
);
  